from dataclasses import dataclass
from typing import List

from messages.base import BaseMessage


@dataclass
class Offer(BaseMessage):
    parking_id: str
    price: int
    distance: float


@dataclass
class ConsolidatedOffers(BaseMessage):
    offers: List[Offer]

    def dict(self):
        return {
            "offers": [offer.dict() for offer in self.offers]
        }
