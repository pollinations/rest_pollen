from typing import List, Optional, Union

from pydantic import BaseModel


class PollenRequest(BaseModel):
    image: str
    input: dict
    token: Optional[str]


class PollenResponse(BaseModel):
    image: str
    input: dict
    output: Optional[Union[dict, List, str, int, float]]
    status: Optional[str]
    cid: Optional[str]
