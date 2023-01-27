import inspect
import json
import subprocess
import time
from typing import List
from urllib.error import URLError
from urllib.request import urlopen

import click
import replicate
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from rest_pollen.apis.wedatanation import app as wedatanation_app
from rest_pollen.authentication import (
    TokenPayload,
    create_api_token,
    get_api_tokens,
    get_current_user,
    get_token_payload,
    revoke_api_token,
)
from rest_pollen.db_client import (
    create_prediction_or_fetch,
    get_from_db,
    run_model,
    save_to_db,
    table_name,
)
from rest_pollen.s3_wrapper import s3store
from rest_pollen.schema import APIToken, PollenRequest, PollenResponse

load_dotenv()


app = FastAPI()


app.mount("/wedatanation", wedatanation_app)
app.mount("/static", StaticFiles(directory="_static"), name="static")


origins = [
    "http://localhost:*",
    "http://localhost:3000",
    "https://pollinations.ai",
    "https://dreamachine-git-nodes-cooles-team.vercel.app/",
    "https://*.pollinations.ai",
    "wss://*",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"healthy": "yes"}


@app.get("/user")
def whoami(user: TokenPayload = Depends(get_current_user)):
    return user


@app.post("/store")
async def store_object(request: Request) -> str:
    data = await request.json()
    cid = s3store.put(data)
    return cid


@app.get("/store/{cid}")
def get(cid: str):
    data = s3store.get(cid)
    return data


@app.get("/store/{cid}/{keys:path}")
def lookup(cid: str, keys: str):
    data = s3store.get(cid, keys)
    return data


@app.get("/mine/")
def mine(
    user: TokenPayload = Depends(get_current_user),
) -> List[str]:
    """Return the list of pollens that the user has run"""
    _, db_client = get_token_payload(user.token)
    pollen_ids = (
        db_client.table(table_name)
        .select("input")
        .eq("user_id", user.sub)
        .execute()
        .data
    )
    return [i["input"] for i in pollen_ids]


@app.get("/token/")
def get_my_tokens(
    user: TokenPayload = Depends(get_current_user),
) -> List[APIToken]:
    """Return the list of API tokens for the user"""
    tokens = get_api_tokens(user.sub)
    return [APIToken(token=t["token"], created_at=t["created_at"]) for t in tokens]


@app.post("/token/")
def create_my_token(
    user: TokenPayload = Depends(get_current_user),
) -> APIToken:
    """Create a new API token for the user"""
    token = create_api_token(user.sub)
    return APIToken(token=token, created_at=time.time())


@app.delete("/token/{token}")
def revoke_my_token(
    token: str,
    user: TokenPayload = Depends(get_current_user),
) -> None:
    """Revoke an API token for the user"""
    revoke_api_token(user.sub, token)
    return


index_repo = "https://raw.githubusercontent.com/pollinations/model-index/main"


@app.get("/models")
def models() -> List[str]:
    """Check the models available on the backend by fetching the models from
    https://raw.githubusercontent.com/pollinations/model-index/main/images.json"""
    with urlopen(f"{index_repo}/images.json") as response:
        models = json.loads(response.read())
    return list(models.keys())


@app.get("/models/{author}/{model}")
def model(author: str, model: str) -> dict:
    try:
        with urlopen(f"{index_repo}/{author}/{model}/inspect.json") as response:
            inspect = json.loads(response.read())
            try:
                openapi = json.loads(
                    inspect[0]["ContainerConfig"]["Labels"][
                        "org.cogmodel.openapi_schema"
                    ]
                )
            except KeyError:
                openapi = json.loads(
                    inspect[0]["Config"]["Labels"]["org.cogmodel.openapi_schema"]
                )
            return openapi
    except URLError:
        raise HTTPException(status_code=404, detail="Model not found")


@app.get("/docs/{author}/{model}", include_in_schema=False)
async def custom_swagger_ui_html(author: str, model: str):
    try:
        return get_swagger_ui_html(
            openapi_url=f"{app.root_path}/models/{author}/{model}",
            title=f"{author}/{model} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )
    except URLError:
        raise HTTPException(status_code=404, detail="Model not found")


@app.get("/redoc/{author}/{model}", include_in_schema=False)
async def redoc_html(author: str, model: str):
    return get_redoc_html(
        openapi_url=f"{app.root_path}/models/{author}/{model}",
        title=f"{author}/{model} -  ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.post("/pollen")
def generate(
    pollen_request: PollenRequest, user: TokenPayload = Depends(get_current_user)
) -> PollenResponse:
    """Generate a pollen on one of the backends.
    Always check the database first for cached results."""
    print(pollen_request)
    if pollen_request.token is None:
        pollen_request.token = user.token
    if is_replicate_backend(pollen_request):
        return run_on_replicate(pollen_request)
    else:
        return run_on_pollinations_infrastructure(pollen_request)


@app.websocket("/ws")
async def websocket_endpoint_pollinations(websocket: WebSocket, token: str = None):
    try:
        user = await get_current_user(token)
        assert user.token is not None
    except HTTPException:
        await websocket.close()
        return
    await websocket.accept()
    # First get the request json
    pollen_request_json = await websocket.receive_json()
    pollen_request = PollenRequest(**pollen_request_json, token=user.token)
    if is_replicate_backend(pollen_request):
        await run_ws_on_replicate(pollen_request, token, websocket)
    else:
        await run_ws_on_pollinations_infrastructure(pollen_request, token, websocket)


async def run_ws_on_replicate(
    pollen_request: PollenRequest, token: str, websocket: WebSocket
):
    cid, output = get_from_db(pollen_request)
    exists_in_db = False
    if output is not None:
        exists_in_db = True
        pollen_response = PollenResponse(
            image=pollen_request.image,
            input=pollen_request.input,
            output=output,
            status="success",
            cid=cid,
        )
        print("Sending from DB")
        await websocket.send_json(pollen_response.dict())
    else:
        model_image = pollen_request.image.replace("replicate:", "")
        model = replicate.models.get(model_image).versions.list()[0]
        prediction = replicate.predictions.create(
            version=model, input=pollen_request.input
        )
        try:
            while True:
                prediction.reload()
                pollen_response = PollenResponse(
                    image=pollen_request.image,
                    input=pollen_request.input,
                    output=prediction.output,
                    status=prediction.status,
                    logs=prediction.logs,
                )
                await websocket.send_json(pollen_response.dict())
                # exit if the prediction is done
                if prediction.status not in ["starting", "processing"]:
                    break
                time.sleep(1)
        except WebSocketDisconnect:
            prediction.cancel()

    if not exists_in_db:
        save_to_db(cid, pollen_response, token)
    await websocket.close()


async def run_ws_on_pollinations_infrastructure(
    pollen_request: PollenRequest, token, websocket: WebSocket
):
    if not pollen_request.image.startswith(
        "614871946825.dkr.ecr.us-east-1.amazonaws.com/"
    ):
        pollen_request.image = (
            "614871946825.dkr.ecr.us-east-1.amazonaws.com/" + pollen_request.image
        )

    cid, output = get_from_db(pollen_request)
    exists_in_db = False
    if output is not None:
        exists_in_db = True
        pollen_response = PollenResponse(
            image=pollen_request.image,
            input=pollen_request.input,
            output=output,
            status="success",
            cid=cid,
        )
        print("Sending from DB")
        await websocket.send_json(pollen_response.dict())
    else:
        prediction, cid, status, queue_position = create_prediction_or_fetch(
            pollen_request.image,
            pollen_request.input,
            pollen_request.token,
            delete_if_failed=True,
        )
        logs = None
        if prediction is not None:
            logs = prediction.get("log")
        while status not in ["success", "failed"]:
            prediction, cid, status, queue_position = create_prediction_or_fetch(
                pollen_request.image, pollen_request.input, pollen_request.token
            )
            pollen_response = PollenResponse(
                image=pollen_request.image,
                input=pollen_request.input,
                output=prediction,
                status=status,
                queue_position=queue_position,
                logs=logs,
            )
            await websocket.send_json(pollen_response.dict())
            # exit if the prediction is done
            if status in ["success", "failed"]:
                break
            time.sleep(1)

    if not exists_in_db:
        save_to_db(cid, pollen_response, token)
    await websocket.close()


def is_replicate_backend(pollen_request: PollenRequest) -> bool:
    return "replicate:" in pollen_request.image


def run_on_pollinations_infrastructure(pollen_request: PollenRequest) -> PollenResponse:
    if not pollen_request.image.startswith(
        "614871946825.dkr.ecr.us-east-1.amazonaws.com/"
    ):
        pollen_request.image = (
            "614871946825.dkr.ecr.us-east-1.amazonaws.com/" + pollen_request.image
        )
    attempt = 0
    response = None
    status = "failed"
    cid = None
    while attempt < 3 and status == "failed":
        try:
            response, cid, status = run_model(
                pollen_request.image, pollen_request.input, pollen_request.token
            )
            response = response["output"]
            status = status
        except (subprocess.CalledProcessError, TypeError):
            pass
        attempt += 1
    if response is not None:
        logs = response["log"]
    pollen_response = PollenResponse(
        image=pollen_request.image,
        input=pollen_request.input,
        output=response,
        status=status,
        cid=cid,
        logs=logs,
    )
    return pollen_response


def run_on_replicate(pollen_request: PollenRequest) -> PollenResponse:
    cid, output = get_from_db(pollen_request)
    exists_in_db = False
    if output is not None:
        exists_in_db = True
    else:
        output = run_with_replicate(pollen_request)
    pollen_response = PollenResponse(
        image=pollen_request.image,
        input=pollen_request.input,
        output=output,
        status="success",
        cid=cid,
    )
    if not exists_in_db:
        save_to_db(cid, pollen_response, pollen_request.token)
    return pollen_response


def run_with_replicate(pollen_request: PollenRequest) -> PollenResponse:
    model_name = pollen_request.image.split(":")[1]
    model = replicate.models.get(model_name)
    output = model.predict(**pollen_request.input)
    if inspect.isgenerator(output):
        output = list(output)
    return output


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to listen on")
@click.option("--port", default=5000, help="Port to listen on")
def main(host: str, port: int) -> None:
    """
    Run the server.
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
