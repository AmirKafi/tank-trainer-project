from datetime import datetime
from enum import Enum
from dateutil.relativedelta import *

from config import MEMBER_PREMIUM_COST, MEMBER_PREMIUM_Period_Month
from exceptions.BaseException import CanNotAddNegativeAmountError, AlreadyPremiumError, NotEnoughBudgetError


class MembershipType(Enum):
    REGULAR = "regular"
    PREMIUM = "premium"


class Member:
    def __init__(self, first_name, last_name, phone_number, membership_type=MembershipType.REGULAR):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.membership_type = membership_type
        self.membership_expiry = None
        self.balance = 0

    def add_to_balance(self, budget: int):
        if budget < 0:
            raise CanNotAddNegativeAmountError()
        if self.balance is None:
            self.balance = 0  # Reset to a valid integer value if somehow set to None

        self.balance += budget

    def set_vip(self):
        if self.membership_type == MembershipType.PREMIUM:
            raise AlreadyPremiumError()
        if self.balance < MEMBER_PREMIUM_COST:
            raise NotEnoughBudgetError()
        self.balance -= MEMBER_PREMIUM_COST
        self.membership_expiry = datetime.now() + relativedelta(months=+ MEMBER_PREMIUM_Period_Month)
        self.membership_type = MembershipType.PREMIUM
