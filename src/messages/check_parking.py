from pydantic import BaseModel


class CheckParking(BaseModel):
    """Message to check parking availability in specified time slot"""

    time_start: int
    time_stop: int
