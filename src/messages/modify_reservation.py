from pydantic import BaseModel


class ModifyReservation(BaseModel):
    """Message from RegionalCoordinator to Parking
    to modify a reservation to new time slot"""

    time_start: int
    time_stop: int
    reservation_id: str
    user_id: str
    parking_id: str
