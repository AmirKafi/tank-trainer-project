from abc import ABC, abstractmethod
from datetime import datetime

from adapters.repositories.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.models.PaymentModels import Payment


class AbstractPaymentRepository(ABC):

    @abstractmethod
    def add_payment(self, payment:Payment):
        raise NotImplementedError

    @abstractmethod
    def get_payments_by_dates(self,member_id:int,start_date:datetime, end_date:datetime):
        raise NotImplementedError

class PaymentRepository(AbstractSqlAlchemyRepository,AbstractPaymentRepository):
    def __init__(self,session):
        self.session = session
        self.seen = set[Payment]
        super().__init__(session,Payment)

    def add_payment(self, payment:Payment):
        super().add(payment)

    def get_payments_by_dates(self,member_id:int,start_date:datetime, end_date:datetime):
        query = self.session.query(Payment)
        payments = query.filter(Payment.member_id == member_id)
        return payments
