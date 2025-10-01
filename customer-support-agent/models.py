from pydantic import BaseModel
from typing import Optional


class UserAccountContext(BaseModel):

    name: str
    customer_id: int
    tier: str = "basic"
    email: Optional[str] = None


class InputGuardRailOutput(BaseModel):

    reason: str
    is_off_topic: bool
