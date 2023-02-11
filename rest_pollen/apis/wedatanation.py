import os
from typing import List, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rest_pollen.apis.avatar_search import find_avatar
from rest_pollen.authentication import (
    TokenPayload,
    get_current_user,
    get_token_payload,
    supabase,
)

app = FastAPI()


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
    images = find_avatar(avatar_request.description, avatar_request.num_suggestions)
    pollen_response = AvatarResponse(
        description=avatar_request.description,
        num_suggestions=avatar_request.num_suggestions,
        user_id=avatar_request.user_id,
        images=images,
        reserved=False,
    )
    return pollen_response


def mark_img_used(img_path, user_id, db_client):
    supabase.table(table_name).insert(
        {"img_url": img_path, "user_id": user_id}
    ).execute()


@app.post("/avatar/reserve")
async def mark_as_used(
    avatar: AvatarResponse, user: TokenPayload = Depends(get_current_user)
):
    _, db_client = get_token_payload(user.token)
    for image in avatar.images:
        mark_img_used(f"url:{image}", avatar.user_id, db_client)
    avatar.reserved = True
    return avatar
