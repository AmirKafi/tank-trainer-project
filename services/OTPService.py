import random
from collections import defaultdict
from datetime import datetime, timedelta

from config import OTP_EXPIRY_MINUTES, OTP_REQUEST_LIMIT_PER_2_MINUTES, OTP_REQUEST_LIMIT_PER_HOUR
from exceptions.BaseException import NotValidPhoneNumberError, NoOTPRequestError, OTPExpiredError, \
    InvalidOTPError, OTPMaximumRequestInTwoMinutesError, OTPMaximumRequestInOneHourError
from helpers.PhoneNumberValidation import is_valid_mobile

otp_store = {}
otp_requests = defaultdict(list)

class SMSProviderInterface:
    def send_otp(self, otp, phone_number):
        raise NotImplementedError()

class KaveNegarProvider(SMSProviderInterface):
    def send_otp(self, otp, phone_number):
        print(f"KaveNegar: Sending OTP to {phone_number}")
        if random.choice([True, False]):
            raise Exception("KaveNegar is down!")

class SignalProvider(SMSProviderInterface):

    def send_otp(self, otp,phone_number):
        print(f"Signal: Sending OTP to {phone_number}")
        if random.choice([True, False]):
            raise Exception("Signal is down!")

class CircuitBreaker:
    def __init__(self, providers):
        self.providers = providers
        self.current_provider_index = 0

    def send_otp(self, otp, phone_number):
        for _ in range(len(self.providers)):
            provider = self.providers[self.current_provider_index]
            try:
                provider.send_otp(otp, phone_number)
                return
            except Exception as e:
                print(e)
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        print("All providers are currently unavailable.")



def check_throttling(phone_number):
    now = datetime.now()

    otp_requests[phone_number] = [t for t in otp_requests[phone_number] if t > now - timedelta(hours=1)]

    if len(otp_requests[phone_number]) >= OTP_REQUEST_LIMIT_PER_HOUR:
        raise OTPMaximumRequestInOneHourError()

    if len([t for t in otp_requests[phone_number] if
            t > now - timedelta(minutes=2)]) >= OTP_REQUEST_LIMIT_PER_2_MINUTES:
        raise OTPMaximumRequestInTwoMinutesError()

    otp_requests[phone_number].append(now)

# OTP generation and storage
def generate_otp(phone_number:str):
    # Add to the request dict and raise error if violates rules
    check_throttling(phone_number)

    if not is_valid_mobile(phone_number):
        raise Exception("Invalid mobile number!")

    otp = random.randint(100000, 999999)
    expiration_time = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    otp_store[phone_number] = {"otp": otp, "expires": expiration_time}

    # Send OTP using circuit breaker
    providers = [KaveNegarProvider(), SignalProvider()]
    circuit_breaker = CircuitBreaker(providers)
    circuit_breaker.send_otp(otp, phone_number)

    print(f"OTP Verification Code: {otp}")

# Verify OTP
def verify_otp(phone_number:str, user_otp:int):

    if not is_valid_mobile(phone_number):
        raise NotValidPhoneNumberError()

    if phone_number not in otp_store:
        raise NoOTPRequestError()

    otp_data = otp_store[phone_number]
    if datetime.now() > otp_data["expires"]:
        del otp_store[phone_number]
        raise OTPExpiredError()

    if otp_data["otp"] == user_otp:
        del otp_store[phone_number]
        return True, "OTP verified successfully!"
    else:
        raise InvalidOTPError()
