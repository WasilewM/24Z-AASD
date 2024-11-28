from dataclasses import dataclass


@dataclass
class ModifyReservation:
    time_start: int  # assume timestamp
    time_stop: int  # assume timestamp
    reservation_id: str
    user_id: str
