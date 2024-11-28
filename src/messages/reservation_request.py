from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class RequestReservation(BaseMessage):
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
    parking_id: str
