from dataclasses import asdict, dataclass


@dataclass
class BaseMessage:
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}
