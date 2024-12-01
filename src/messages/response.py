from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ReservationResponse(BaseMessage):
    """Message from Parking to RegionalCoordinator
    and from RegionalCoordinator to User
    about the success of the reservation or modification"""
    success: bool
    user_id: str
    reservation_id: str
