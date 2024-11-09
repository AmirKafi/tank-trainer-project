from pydantic.dataclasses import dataclass


class BaseExceptions(Exception):
    pass

@dataclass
class NotValidPhoneNumberError(BaseExceptions):
    message: str = "Invalid Phone Number...!"

    def __str__(self):
        return self.message

@dataclass
class OTPExpiredError(BaseExceptions):
    message: str = "OTP has expired!"

    def __str__(self):
        return self.message


@dataclass
class NoOTPRequestError(BaseExceptions):
    message: str = "No OTP request found for this phone number!"

    def __str__(self):
        return self.message

@dataclass
class InvalidOTPError(BaseExceptions):
    message: str = "Invalid OTP!"
    def __str__(self):
        return self.message

@dataclass
class MemberDoesNotExistError(BaseExceptions):
    message: str = "Member does not exist , please submit first!"

    def __str__(self):
        return self.message

@dataclass
class CanNotAddNegativeAmountError(BaseExceptions):
    message: str = "the amount you want to add to your balance must be greater than zero ."
    def __str__(self):
        return self.message

@dataclass
class AlreadyPremiumError(BaseExceptions):
    message: str = "You are already a premium!"
    def __str__(self):
        return self.message

@dataclass
class NotEnoughBudgetError(BaseExceptions):
    message: str = "You have not enough budget!"
    def __str__(self):
        return self.message

@dataclass
class MaximumRegularMemberError(BaseExceptions):
    message:str = 'Maximum reservation time for regular members is 7 days'
    def __str__(self):
        return self.message

@dataclass
class MaximumPremiumMemberError(BaseExceptions):
    message:str = 'Maximum reservation time for premium members is 14 days.'
    def __str__(self):
        return self.message

@dataclass
class BookIsReservedError(BaseExceptions):
    message:str = 'Book is reserved!'
    def __str__(self):
        return self.message
@dataclass
class OTPMaximumRequestInOneHourError(BaseExceptions):
    message:str = "Too many OTP requests in the last hour"
    def __str__(self):
        return self.message

@dataclass
class OTPMaximumRequestInTwoMinutesError(BaseExceptions):
    message:str = "Too many OTP requests in the last 2 minutes"
    def __str__(self):
        return self.message