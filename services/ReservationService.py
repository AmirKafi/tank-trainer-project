from config import RESERVATION_MINIMUM_PAYMENT_FOR_DISCOUNT, \
    RESERVATION_MINIMUM_BOOKS_COUNT_FOR_DISCOUNT
from domains.adapters.repositories.BookRepository import BookRepository
from domains.adapters.repositories.MemberRepository import MemberRepository
from domains.adapters.repositories.PaymentRepository import PaymentRepository
from domains.adapters.repositories.ReservationRepository import ReservationRepository
from events import ReserveBookCommand
from exceptions.BaseException import MaximumRegularMemberError, MaximumPremiumMemberError, BookIsReservedError
from domains.models.BookManagementModels import Reservation, ReservationStatus
from domains.models.MemberManagementModels import MembershipType
from services.UnitOfWork import UnitOfWork


def reserve_service(uow:UnitOfWork,cmd:ReserveBookCommand):
    with uow:
        try:
            repo = uow.get_repository(ReservationRepository)
            book_repo = uow.get_repository(BookRepository)
            member_repo = uow.get_repository(MemberRepository)
            payment_repo = uow.get_repository(PaymentRepository)

            reservation = Reservation(
                cmd.book_id,
                cmd.member_id,
                cmd.duration
            )

            book = book_repo.get_book_by_id(cmd.book_id)
            if book.status == ReservationStatus.RESERVED:
                raise BookIsReservedError()

            member = member_repo.get_member_by_id(cmd.member_id)
            payments = payment_repo.get_payments_by_dates(cmd.member_id, reservation.start_date, reservation.end_date)
            total_cost = calculate_reservation_cost(member, book, cmd.duration, payments)
            reservation.set_total_cost(total_cost)
            new_reservation = repo.reserve(reservation)
            book_repo.set_to_reserved(book, new_reservation.id)
            return new_reservation
        except Exception as error:
            raise error

def get_reserved_books_service(uow:UnitOfWork,member_id:int):
    with uow:
        repo = uow.get_repository(ReservationRepository)
        books = repo.get_reserved_books(member_id)
        return books

def calculate_reservation_cost(member, book, duration,payments):

    if member.membership_type == MembershipType.PREMIUM:
        # Premium users can reserve books up to 14 days and it's free
        if duration <= 14:
            print("Im Here")
            return 0
        else:
            raise MaximumPremiumMemberError()

    elif member.membership_type == MembershipType.REGULAR:

        if duration > 7:
            raise MaximumRegularMemberError()

        # Regular users must pay
        cost_per_day = book.price
        total_cost = cost_per_day * duration

        # Apply discount if there is any
        discount = calculate_discount(member,payments)
        total_cost *= (1 - discount)

        return total_cost
    else:
        raise Exception("error")

def calculate_discount(member,payments):
    # Check for reserved books in a month
    if len(member.reservations) > RESERVATION_MINIMUM_BOOKS_COUNT_FOR_DISCOUNT:
        return 0.3  # 30% discount

    # calc total spent in the past 2 month
    total_spent_last_2_months = sum(res.amount for res in payments)
    if total_spent_last_2_months > RESERVATION_MINIMUM_PAYMENT_FOR_DISCOUNT:
        return 1.0  # Free
    return 0.0