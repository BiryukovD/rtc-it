from pydantic import BaseModel
from typing import Optional

class Parameters(BaseModel):
    username: str
    password: str
    vlan: Optional[int]
    interfaces: list[int]


class Device(BaseModel):
    timeoutInSeconds: int
    parameters: Parameters