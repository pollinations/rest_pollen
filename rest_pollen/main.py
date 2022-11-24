import click
import replicate
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypollsdk.model import run_model

from rest_pollen.apis.wedatanation import app as wedatanation_app
from rest_pollen.authentication import TokenPayload, get_current_user

load_dotenv()

app = FastAPI()


app.mount("/wedatanation", wedatanation_app)


class PollenRequest(BaseModel):
    image: str
    input: dict


class PollenResponse(BaseModel):
    image: str
    input: dict
    output: dict


origins = [
    "http://localhost:*",
    "http://localhost:3000",
    "https://pollinations.ai",
    "https://*.pollinations.ai",
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
async def root():
    return {"healthy": "yes"}


@app.get("/user")
async def whoami(user: TokenPayload = Depends(get_current_user)):
    return user


@app.post("/pollen")
async def generate(
    pollen_request: PollenRequest, user: TokenPayload = Depends(get_current_user)
) -> PollenResponse:
    if is_pollinations_backend(pollen_request):
        return run_on_pollinations_infrastructure(pollen_request)
    elif "replicate:" in pollen_request.image:
        return run_on_replicate(pollen_request)
    else:
        raise HTTPException(status_code=400, detail="Unknown model backend")


def is_pollinations_backend(pollen_request: PollenRequest) -> bool:
    return "amazonaws" in pollen_request.image


def run_on_pollinations_infrastructure(pollen_request: PollenRequest) -> PollenResponse:
    response = run_model(pollen_request.image, pollen_request.input)
    pollen_response = PollenResponse(
        image=pollen_request.image,
        input=pollen_request.input,
        output=response["output"],
    )
    return pollen_response


def run_on_replicate(pollen_request: PollenRequest) -> PollenResponse:
    model_name = pollen_request.image.split(":")[1]
    model = replicate.models.get(model_name)
    output = model.predict(**pollen_request.input)
    pollen_response = PollenResponse(
        image=pollen_request.image, input=pollen_request.input, output=output
    )
    return pollen_response


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
