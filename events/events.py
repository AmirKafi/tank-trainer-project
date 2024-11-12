from dataclasses import dataclass


class Event:
    pass


@dataclass
class OTPSendEvent(Event):
    phone_number: str = None
