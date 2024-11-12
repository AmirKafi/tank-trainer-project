import json
from collections.abc import Callable
from dataclasses import asdict
from json import JSONEncoder

from events.events import OTPSendEvent
from services.OTPService import generate_otp


def publish_otp_event(
        event: OTPSendEvent(),
        publish: Callable
):
    publish("otp_request",JSONEncoder().encode(asdict(event)))


def send_otp_handler(
        event: OTPSendEvent
):
    generate_otp(event.phone_number)
