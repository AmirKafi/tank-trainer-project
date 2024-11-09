from abc import abstractmethod,ABC

from sqlalchemy.orm import Session

from domains.adapters.repositories.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.models.MemberManagementModels import Member


class AbstractMemberRepository(ABC):

    @abstractmethod
    def get_members_list(self):
        raise NotImplementedError

    @abstractmethod
    def add_member(self, member:Member)-> Member:
        raise NotImplementedError

    @abstractmethod
    def get_member_by_id(self,member_id):
        raise NotImplementedError

    @abstractmethod
    def get_member_by_phone_number(self,phone_number:str)-> Member:
        raise NotImplementedError

    @abstractmethod
    def add_to_balance(self,member_id,amount:int)-> None:
        raise NotImplementedError

    @abstractmethod
    def set_vip(self, member_id: int):
        raise NotImplementedError


class MemberRepository(AbstractSqlAlchemyRepository,AbstractMemberRepository):
    def __init__(self,session:Session):
        super().__init__(session,Member)

    def get_members_list(self):
        members = super().list()
        return members

    def add_member(self, member:Member)-> Member:
        super().add(member)
        return member

    def get_member_by_id(self,member_id):
        member = super().get(member_id)
        return member

    def get_member_by_phone_number(self,phone_number:str)-> Member:
        query = self.session.query(Member)
        member = query.filter(Member.phone_number == phone_number).first()
        return  member

    def add_to_balance(self,member_id:int,amount:int)-> None:
        member = super().get(member_id)
        member.add_to_balance(amount)
        super().add(member)

    def set_vip(self,member_id:int):
        member = super().get(member_id)
        member.set_vip()
        super().add(member)
