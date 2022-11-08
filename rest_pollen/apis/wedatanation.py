from typing import List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypollsdk.model import run_model

from rest_pollen.authentication import TokenPayload, get_current_user

app = FastAPI()

AVATAR_IMAGE = (
    "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/wedatanation-pick-avatar"
)
INDEX_ZIP = "https://pollinations-ci-bucket.s3.amazonaws.com/clip-index.zip"


class AvatarRequest(BaseModel):
    description: str
    num_suggestions: int
    user_id: str


class AvatarResponse(BaseModel):
    description: str
    num_suggestions: int
    user_id: str
    images: List[str]
    reserved: bool


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
    response = run_model(
        AVATAR_IMAGE,
        {
            "index_zip": INDEX_ZIP,
            "prompt": avatar_request.description,
            "user_id": avatar_request.user_id,
        },
    )
    pollen_response = AvatarResponse(
        input=avatar_request.input,
        output=response["output"],
    )
    return pollen_response


@app.post("/avatar/reserve")
async def mark_as_used(avatar: AvatarResponse):
    avatar.reserved = True
    return avatar
