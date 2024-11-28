from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ModifyReservation(BaseMessage):
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
    reservation_id: str
    user_id: str
