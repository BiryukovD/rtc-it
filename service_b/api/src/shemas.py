from typing import Optional

from pydantic import BaseModel


class Parameters(BaseModel):
    username: str
    password: str
    vlan: Optional[int]
    interfaces: list[int]


class Config(BaseModel):
    timeoutInSeconds: int
    parameters: Parameters