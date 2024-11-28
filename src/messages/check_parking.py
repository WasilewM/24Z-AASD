from dataclasses import dataclass


@dataclass
class CheckParking:
    x: int
    y: int
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
