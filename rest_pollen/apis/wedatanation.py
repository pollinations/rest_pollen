import os
from typing import List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rest_pollen.authentication import TokenPayload, get_current_user
from rest_pollen.db_client import get_authenticated_client, run_model

app = FastAPI()


AVATAR_IMAGE = (
    "614871946825.dkr.ecr.us-east-1.amazonaws.com/pollinations/wedatanation-pick-avatar"
)
INDEX_ZIP = "url:https://pollinations-ci-bucket.s3.amazonaws.com/clip-index.zip"

table_name = os.environ.get("wedatanation_avatar_table", "wedatanation-avatar-dev")


class AvatarRequest(BaseModel):
    description: str
    num_suggestions: int
    user_id: str


class AvatarResponse(BaseModel):
    description: Optional[str]
    num_suggestions: Optional[int]
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
            "num_results": avatar_request.num_suggestions,
            "table_name": table_name,
            "ignore_cache": uuid4().hex,  # On a new request, we don't want to return the same avatar
        },
        token=user.token,
    )
    images = [i for i in response["output"]["images"].split("url:") if i != ""]
    pollen_response = AvatarResponse(
        description=avatar_request.description,
        num_suggestions=avatar_request.num_suggestions,
        user_id=avatar_request.user_id,
        images=images,
        reserved=False,
    )
    return pollen_response


def mark_img_used(img_path, user_id, db_client):
    db_client.table(table_name).insert(
        {"img_url": img_path, "user_id": user_id}
    ).execute()


@app.post("/avatar/reserve")
async def mark_as_used(
    avatar: AvatarResponse, user: TokenPayload = Depends(get_current_user)
):
    db_client = get_authenticated_client(user.token)
    for image in avatar.images:
        mark_img_used(f"url:{image}", avatar.user_id, db_client)
    avatar.reserved = True
    return avatar
