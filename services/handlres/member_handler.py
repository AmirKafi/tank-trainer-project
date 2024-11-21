from adapters.repositories.MemberRepository import MemberRepository
from adapters.repositories.PaymentRepository import PaymentRepository
from domains.models.MemberManagementModels import Member
from domains.models.PaymentModels import Payment
from events.commands import CreateMemberCommand, AddToMemberBalanceCommand, SetMemberVIPCommand
from exceptions.BaseException import MemberDoesNotExistError
from services.UnitOfWork import UnitOfWork


def add_member_handler(
        cmd:CreateMemberCommand,
        uow:UnitOfWork
)->Member:
    with uow:
        repo = uow.get_repository(MemberRepository)
        new_member = Member(
            cmd.first_name,
            cmd.last_name,
            cmd.phone_number
        )
        repo.add_member(new_member)
        uow.commit()
        return new_member

def get_member_by_phone_number_handler(uow:UnitOfWork, phone_number:str):
    with uow:
        repo = uow.get_repository(MemberRepository)
        member = repo.get_member_by_phone_number(phone_number)
        if not member:
            raise MemberDoesNotExistError()
        member_data = {
            "id": member.id,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "phone_number": member.phone_number,
            "membership_type": member.membership_type,
            "membership_expiry": member.membership_expiry,
            "balance": member.balance
        }
        return member_data

def add_to_balance_handler(
        cmd:AddToMemberBalanceCommand,
        uow: UnitOfWork()):
    with uow:
        repo = uow.get_repository(MemberRepository)
        payment_repo = uow.get_repository(PaymentRepository)
        payment_repo.add_payment(Payment(cmd.amount,cmd.member_id))
        repo.add_to_balance(cmd.member_id,cmd.amount)

def set_to_vip_handler(
        cmd:SetMemberVIPCommand,
        uow:UnitOfWork()
):
    with uow:
        repo = uow.get_repository(MemberRepository)
        repo.set_vip(cmd.member_id)