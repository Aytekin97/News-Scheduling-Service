from pydantic import BaseModel
from typing import List
from datetime import time


class JobCreate(BaseModel):
    frequency: str  # "daily", "weekly", "bi-weekly"
    run_time: str   # or we can parse "HH:MM" into a time object
    number_of_days: int
    list_of_companies: List[str]

class JobRead(BaseModel):
    id: int
    frequency: str
    run_time: str
    number_of_days: int
    list_of_companies: List[str]
    status: str
    # next_run_time: str  # if you want to display it

    class Config:
        orm_mode = True
