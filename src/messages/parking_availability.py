from pydantic import BaseModel


class ParkingAvailable(BaseModel):
    """Message from Parking to RegionalCoordinator
    about parking availability, price and location"""

    parking_id: str
    parking_price: int
    parking_x: int
    parking_y: int
    available: bool
