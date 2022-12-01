import os

import requests
from dotenv import load_dotenv
from supabase import Client, create_client

from rest_pollen.schema import PollenRequest, PollenResponse

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
supabase: Client = None
if url is not None and supabase_api_key is not None:
    supabase = create_client(url, supabase_api_key)
store_url = "https://store.pollinations.ai"


def store(data: dict):
    data = remove_none(data)
    response = requests.post(f"{store_url}/", json=data)
    response.raise_for_status()
    cid = response.text
    return cid


def get_from_db(pollen_request: PollenRequest) -> PollenResponse:
    cid = store(pollen_request.dict())
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
            output = response.json().get("output")
            output = adjust_format(output)
        except requests.exceptions.HTTPError:
            pass
    return cid, output


def save_to_db(input_cid: str, pollen_response: PollenResponse):
    output_cid = store(pollen_response.dict())
    db_entry = (
        supabase.table("pollen")
        .update({"output": output_cid, "end_time": "now()", "success": True})
        .eq("input", input_cid)
        .execute()
    )
    return db_entry.data[0]


def adjust_format(data):
    if isinstance(data, list):
        return [adjust_format(x) for x in data]
    elif isinstance(data, dict):
        if "0" in data:
            return [adjust_format(data[k]) for k in sorted(data.keys()) if k.isdigit()]
        else:
            return {k: adjust_format(v) for k, v in data.items() if k != ".cid"}
    else:
        return data


def remove_none(data):
    if isinstance(data, dict):
        return {k: remove_none(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_none(v) for v in data if v is not None]
    else:
        return data
