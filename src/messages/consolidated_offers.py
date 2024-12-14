from typing import List

from pydantic import BaseModel


class Offer(BaseModel):
    parking_id: str
    price: int
    distance: float


class ConsolidatedOffers(BaseModel):
    """Message with best offers in respond to User's CheckOffers message"""

    offers: List[Offer]
