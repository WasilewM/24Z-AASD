from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ModifyReservation(BaseMessage):
    """Message from RegionalCoordinator to Parking
    to modify a reservation to new time slot"""
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
    reservation_id: str
    user_id: str
