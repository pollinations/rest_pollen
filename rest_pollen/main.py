import click
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rest_pollen.authentication import TokenPayload, get_current_user
from rest_pollen.apis.wedatanation import app as wedatanation_app
from pypollsdk.model import run_model


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
    response = run_model(pollen_request.image, pollen_request.input)
    pollen_response = PollenResponse(
        image=pollen_request.image,
        input=pollen_request.input,
        output=response["output"],
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
