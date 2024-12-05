from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class CheckOffers(BaseMessage):
    """Message from User to RegionalCoordinator
    to check offers for a given position and time range."""

    x: int
    y: int
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
