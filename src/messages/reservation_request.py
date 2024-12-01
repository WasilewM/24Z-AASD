from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class RequestReservation(BaseMessage):
    """Message from User to RegionalCoordinator
    to request a reservation in specified time slot and parking"""
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
    parking_id: str
    user_id: str
