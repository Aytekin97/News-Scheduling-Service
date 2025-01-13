from typing import List, Optional
from pydantic import BaseModel

class JobCreate(BaseModel):
    frequency: str   # e.g. "daily", "hourly" (or a cron-like string if you prefer)
    repeat: bool
    number_of_days: int
    list_of_companies: List[str]

class JobRead(BaseModel):
    id: int
    frequency: str
    repeat: bool
    number_of_days: int
    list_of_companies: List[str]
    status: str
    next_run_time: str

    class Config:
        orm_mode = True