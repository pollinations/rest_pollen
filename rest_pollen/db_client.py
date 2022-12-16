import os
import time

import requests
from dotenv import load_dotenv
from supabase import Client, create_client

from rest_pollen.s3_wrapper import s3store
from rest_pollen.schema import PollenRequest, PollenResponse

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
supabase: Client = None
if url is not None and supabase_api_key is not None:
    supabase = create_client(url, supabase_api_key)
table_name: str = os.environ.get("DB_NAME")
store_url = "https://store.pollinations.ai"


def store(data: dict):
    return s3store.put(data)
    # data = remove_none(data)
    # try:
    #     response = requests.post(f"{store_url}/", json=data, timeout=5)
    #     response.raise_for_status()
    #     cid = response.text
    # except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
    #     cid = s3store.put(data)
    # return cid


def fetch(cid: str):
    if cid.startswith("s3:"):
        data = s3store.get(cid)
    else:
        response = requests.get(f"{store_url}/pollen/{cid}")
        response.raise_for_status()
        data = response.json()
    return data


def get_from_db(pollen_request: PollenRequest) -> PollenResponse:
    cid = store(pollen_request.dict())
    db_entry = (
        supabase.table(table_name)
        .upsert({"input": cid, "image": pollen_request.image})
        .execute()
        .data[0]
    )
    output = None
    if db_entry["success"] is True:
        if db_entry["output"].startswith("s3:"):
            output = s3store.get(db_entry["output"])
        else:
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
        supabase.table(table_name)
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


def run_model(image, inputs, priority=1):
    cid = store({"input": inputs})
    pollen = {
        "image": image,
        "input": cid,
        "priority": priority,
    }
    db_entry = (supabase.table(table_name).upsert(pollen).execute()).data[0]
    if db_entry["success"] is False:
        # delete this row and reinsert it
        db_entry = (
            supabase.table(table_name).delete().eq("input", cid).execute()
        ).data[0]
        db_entry = (supabase.table(table_name).upsert(pollen).execute()).data[0]
    while db_entry["success"] is None:
        db_entry = (
            supabase.table(table_name).select("*").eq("input", cid).execute()
        ).data[0]
        time.sleep(1)
    if db_entry["success"] is True:
        return fetch(db_entry["output"])
    else:
        return None
