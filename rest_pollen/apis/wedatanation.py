import click
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rest_pollen.authentication import TokenPayload, get_current_user

from pypollsdk.model import run_model


load_dotenv()

app = FastAPI()

AVATAR_IMAGE = "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/wedatanation-pick-avatar"
INDEX_CID = ""


class AvatarRequest(BaseModel):
    description: str


class AvatarResponse(BaseModel):
    input: dict
    output: dict


app = FastAPI()


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


@app.post("/avatar")
async def generate(
    avatar_request: AvatarRequest, user: TokenPayload = Depends(get_current_user)
) -> AvatarResponse:
    response = run_model(AVATAR_IMAGE, {
        "index_cid": INDEX_CID,
        "prompt": avatar_request.description
    })
    pollen_response = AvatarResponse(
        input=avatar_request.input,
        output=response["output"],
    )
    return pollen_response
