import time
from typing import List, Optional, Union

import click
import replicate
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypollsdk.model import run_model
from starlette.websockets import WebSocketDisconnect

from rest_pollen.apis.wedatanation import app as wedatanation_app
from rest_pollen.authentication import TokenPayload, get_current_user
from rest_pollen.db_client import supabase

load_dotenv()
store_url = "https://store.pollinations.ai"


app = FastAPI()


app.mount("/wedatanation", wedatanation_app)


class PollenRequest(BaseModel):
    image: str
    input: dict


class PollenResponse(BaseModel):
    image: str
    input: dict
    output: Optional[Union[dict, List, str, int, float]]
    status: Optional[str]


origins = [
    "http://localhost:*",
    "http://localhost:3000",
    "https://pollinations.ai",
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
        image=pollen_request.image, input=pollen_request.input, output=output
    )
    if not exists_in_db:
        save_to_db(cid, pollen_response)
    return pollen_response


def store(data: dict):
    response = requests.post(f"{store_url}/", json=data)
    response.raise_for_status()
    cid = response.text
    return cid


def get_from_db(pollen_request: PollenRequest) -> PollenResponse:
    cid = store(pollen_request.dict()["input"])
    db_entry = (
        supabase.table("pollen")
        .upsert({"input": cid, "image": pollen_request.image})
        .execute()
        .data[0]
    )
    output = None
    if db_entry["success"] is True:
        try:
            response = requests.get(f"{store_url}/pollen/{cid}")
            response.raise_for_status()
            output = response.json()
        except requests.exceptions.HTTPError:
            pass
    return cid, output


def run_with_replicate(pollen_request: PollenRequest) -> PollenResponse:
    model_name = pollen_request.image.split(":")[1]
    model = replicate.models.get(model_name)
    output = model.predict(**pollen_request.input)
    return output


def save_to_db(input_cid: str, pollen_response: PollenResponse):
    output_cid = store(pollen_response.dict()["output"])
    db_entry = (
        supabase.table("pollen")
        .update({"output": output_cid, "end_time": "now()", "success": True})
        .eq("input", input_cid)
        .execute()
    )
    return db_entry.data[0]


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
