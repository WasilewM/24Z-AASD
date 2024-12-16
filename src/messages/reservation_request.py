from pydantic import BaseModel


class RequestReservation(BaseModel):
    """Message from User to RegionalCoordinator
    to request a reservation in specified time slot and parking"""

    time_start: int
    time_stop: int
    parking_id: str
    user_id: str
