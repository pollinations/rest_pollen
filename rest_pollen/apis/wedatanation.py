import os
from collections import defaultdict
from typing import List, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rest_pollen.apis.avatar_search import (
    find_avatar,
    get_all_image_urls,
    get_attributes,
)
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


def extract_image_id_from_url(url):
    return url.split("/")[-1].split("(")[0].split(".")[0]


@app.get("/available")
async def get_available() -> dict:
    """Show how many images are available for each category"""
    # fetch all image ids
    img_urls = get_all_image_urls()
    img_ids = [extract_image_id_from_url(url) for url in img_urls]
    # fetch all reserved image urls
    reserved_img_urls = supabase.table(table_name).select("*").execute().data
    reserved_img_ids = [
        extract_image_id_from_url(url["img_url"]) for url in reserved_img_urls
    ]
    # get the difference
    available_img_ids = set(img_ids) - set(reserved_img_ids)
    # group by animal category using defaultdict with default 0
    available_counts = defaultdict(lambda: 0)
    for img_id in available_img_ids:
        animal, item, attribute = get_attributes(img_id)
        available_counts[animal] += 1
    available_counts["total"] = sum(available_counts.values())
    # return the count for each category
    return available_counts
