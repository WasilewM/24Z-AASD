from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class ParkingAvailable(BaseMessage):
    """Message from Parking to RegionalCoordinator
    about parking availability, price and location"""
    parking_id: str
    parking_price: int
    parking_x: int
    parking_y: int
    available: bool
