from pydantic import BaseModel


class UserAccountContext(BaseModel):
    name: str
    customer_id: int
    tier: str = "base"


class InputGuardRailOutput(BaseModel):
    output_info: str
    tripwire_triggered: bool
