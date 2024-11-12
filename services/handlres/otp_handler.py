from collections.abc import Callable

from events.events import OTPSendEvent
from services.OTPService import generate_otp


def publish_otp_event(
        event: OTPSendEvent,
        publish: Callable
):
    publish("otp_request",event)


def send_otp_handler(
        event: OTPSendEvent
):
    generate_otp(event.phone_number)
