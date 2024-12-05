from dataclasses import dataclass

from messages.base import BaseMessage


@dataclass
class CheckParking(BaseMessage):
    """Message to check parking availability in specified time slot"""

    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
