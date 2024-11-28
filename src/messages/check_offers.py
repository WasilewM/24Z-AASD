from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class CheckOffers(BaseMessage):
    x: int
    y: int
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
