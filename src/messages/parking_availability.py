from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ParkingAvailable(BaseMessage):
    parking_id: str
    parking_price: int
    parking_x: int
    parking_y: int
    available: bool
