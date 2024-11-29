from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ReservationResponse(BaseMessage):
    success: bool
    user_id: str
