from domains.adapters.repositories.MemberRepository import MemberRepository
from domains.adapters.repositories.PaymentRepository import PaymentRepository
from events.commands import CreateMemberCommand, AddToMemberBalanceCommand
from domains.models.MemberManagementModels import Member
from domains.models.PaymentModels import Payment
from services.UnitOfWork import UnitOfWork


def add_member_service(
        uow:UnitOfWork,
        command:CreateMemberCommand
)->Member:
    with uow:
        repo = uow.get_repository(MemberRepository)
        new_member = Member(
            command.first_name,
            command.last_name,
            command.phone_number
        )
        repo.add_member(new_member)
        uow.commit()
        return new_member

def get_members_service(uow:UnitOfWork):
    with uow:
        repo = uow.get_repository(MemberRepository)
        members = repo.get_members_list()
        result = []

        for member in members:
            # Now we can serialize the book with all the author data
            member_data = {
                "id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "phone_number": member.phone_number,
                "membership_type": member.membership_type,
                "membership_expiry":member.membership_expiry,
                "balance": member.balance
            }

            result.append(member_data)

        return result

def get_member_by_phone_number_service(uow:UnitOfWork,phone_number:str):
    with uow:
        repo = uow.get_repository(MemberRepository)
        member = repo.get_member_by_phone_number(phone_number)
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

def add_to_balance_service(
        uow:UnitOfWork,
        member_id:int,
        command:AddToMemberBalanceCommand):
    with uow:
        repo = uow.get_repository(MemberRepository)
        payment_repo = uow.get_repository(PaymentRepository)
        payment_repo.add_payment(Payment(command.amount,member_id))
        repo.add_to_balance(member_id,command.amount)

def set_to_vip_service(uow:UnitOfWork,member_id:int):
    with uow:
        repo = uow.get_repository(MemberRepository)
        repo.set_vip(member_id)
