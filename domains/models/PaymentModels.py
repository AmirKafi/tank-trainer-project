from datetime import datetime

from domains.models.MemberManagementModels import Member


class Payment:
    def __init__(self,amount,member_id:int):
        self.amount = amount
        self.member_id = member_id
        self.payment_date = datetime.now()