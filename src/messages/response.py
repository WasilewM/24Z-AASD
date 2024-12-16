from pydantic import BaseModel


class ReservationResponse(BaseModel):
    """Message from Parking to RegionalCoordinator
    and from RegionalCoordinator to User
    about the success of the reservation or modification"""

    success: bool
    user_id: str
    reservation_id: str
