from pydantic import BaseModel


class CheckOffers(BaseModel):
    """Message from User to RegionalCoordinator
    to check offers for a given position and time range."""

    x: int
    y: int
    time_start: int
    time_stop: int
