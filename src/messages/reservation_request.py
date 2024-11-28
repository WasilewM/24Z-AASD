from dataclasses import dataclass


@dataclass
class RequestReservation:
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
    parking_id: str
