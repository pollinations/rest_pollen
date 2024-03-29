import os
import time

import requests
from dotenv import load_dotenv

from rest_pollen.authentication import get_token_payload
from rest_pollen.s3_wrapper import s3store
from rest_pollen.schema import PollenRequest, PollenResponse

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
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
    data = pollen_request.dict()
    del data["token"]
    cid = store(data)
    user, supabase = get_token_payload(pollen_request.token)
    db_entry = (
        supabase.table(table_name)
        .upsert({"input": cid, "image": pollen_request.image, "user_id": user.sub})
        .execute()
        .data[0]
    )
    output = None
    if db_entry["success"] is True:
        if db_entry["output"].startswith("s3:"):
            output = s3store.get(db_entry["output"])
            if len(output["output"]) == 0:
                output = None
        else:
            try:
                response = requests.get(f"{store_url}/pollen/{cid}")
                response.raise_for_status()
                output = response.json().get("output")
                output = adjust_format(output)
            except requests.exceptions.HTTPError:
                pass
    return cid, output


def save_to_db(input_cid: str, pollen_response: PollenResponse, token: str):
    output_cid = store(pollen_response.dict())
    user, supabase = get_token_payload(token)
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


def run_model(image, inputs, token, priority=1):
    user, supabase = get_token_payload(token)
    cid = store({"input": inputs})
    pollen = {"image": image, "input": cid, "priority": priority, "user_id": user.sub}
    db_entry = (supabase.table(table_name).upsert(pollen).execute()).data[0]
    if db_entry["success"] is False:
        # delete this row and reinsert it
        db_entry = supabase.table(table_name).delete().eq("input", cid).execute()
        db_entry = (supabase.table(table_name).upsert(pollen).execute()).data[0]
    while db_entry["success"] is None:
        db_entry = (
            supabase.table(table_name).select("*").eq("input", cid).execute()
        ).data[0]
        time.sleep(1)
    response = None
    if db_entry["output"] is not None:
        response = fetch(db_entry["output"])
    status = "starting"
    if db_entry["success"] is True:
        status = "success"
    elif db_entry["success"] is False:
        status = "failed"
    return response, cid, status


def get_queue_position(cid):
    return 1


def create_prediction_or_fetch(
    image, inputs, token, priority=1, delete_if_failed=False
):
    user, supabase = get_token_payload(token)
    cid = store({"input": inputs})
    pollen = {"image": image, "input": cid, "priority": priority, "user_id": user.sub}
    db_entry = (supabase.table(table_name).upsert(pollen).execute()).data[0]
    if db_entry["success"] is False and delete_if_failed:
        db_entry = (
            supabase.table(table_name).delete().eq("input", cid).execute()
        ).data[0]
        db_entry = (supabase.table(table_name).upsert(pollen).execute()).data[0]
    response = None
    if db_entry["output"] is not None:
        response = fetch(db_entry["output"])
    status = "starting"
    if db_entry["processing_started"] is True:
        status = "processing"
    if db_entry["success"] is True:
        status = "success"
    elif db_entry["success"] is False:
        status = "failed"
    if db_entry["success"] is None:
        queue_position = get_queue_position(cid)
    else:
        queue_position = None
    return response, cid, status, queue_position
