from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ParkingAvailable(BaseMessage):
    parking_id: str
