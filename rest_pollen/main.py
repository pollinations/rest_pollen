import time

import click
import replicate
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pypollsdk.model import run_model
from starlette.websockets import WebSocketDisconnect

from rest_pollen.apis.wedatanation import app as wedatanation_app
from rest_pollen.authentication import TokenPayload, get_current_user
from rest_pollen.db_client import get_from_db, save_to_db
from rest_pollen.schema import PollenRequest, PollenResponse

load_dotenv()


app = FastAPI()


app.mount("/wedatanation", wedatanation_app)


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


@app.post("/pollen")
def generate(
    pollen_request: PollenRequest, user: TokenPayload = Depends(get_current_user)
) -> PollenResponse:
    if is_pollinations_backend(pollen_request):
        return run_on_pollinations_infrastructure(pollen_request)
    elif is_replicate_backend(pollen_request):
        return run_on_replicate(pollen_request)
    else:
        raise HTTPException(status_code=400, detail="Unknown model backend")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    try:
        user = await get_current_user(token)
        assert user.token is not None
    except HTTPException:
        await websocket.close()
        return
    await websocket.accept()
    # First get the request json
    pollen_request_json = await websocket.receive_json()
    pollen_request = PollenRequest(**pollen_request_json)

    cid, output = get_from_db(pollen_request)
    exists_in_db = False
    if output is not None:
        exists_in_db = True
        pollen_response = PollenResponse(
            image=pollen_request.image,
            input=pollen_request.input,
            output=output,
            status="success",
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
                )
                await websocket.send_json(pollen_response.dict())
                # exit if the prediction is done
                if prediction.status not in ["starting", "processing"]:
                    break
                time.sleep(1)
        except WebSocketDisconnect:
            prediction.cancel()

    if not exists_in_db:
        save_to_db(cid, pollen_response)
    await websocket.close()


def is_pollinations_backend(pollen_request: PollenRequest) -> bool:
    return "amazonaws" in pollen_request.image


def is_replicate_backend(pollen_request: PollenRequest) -> bool:
    return "replicate:" in pollen_request.image


def run_on_pollinations_infrastructure(pollen_request: PollenRequest) -> PollenResponse:
    response = run_model(pollen_request.image, pollen_request.input)
    pollen_response = PollenResponse(
        image=pollen_request.image,
        input=pollen_request.input,
        output=response["output"],
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
    )
    if not exists_in_db:
        save_to_db(cid, pollen_response)
    return pollen_response


def run_with_replicate(pollen_request: PollenRequest) -> PollenResponse:
    model_name = pollen_request.image.split(":")[1]
    model = replicate.models.get(model_name)
    output = model.predict(**pollen_request.input)
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
