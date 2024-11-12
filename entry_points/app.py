import json
import logging
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, Body
from fastapi.encoders import jsonable_encoder

from adapters.repositories.AuthorRepository import AuthorRepository
from adapters.repositories.BookRepository import BookRepository
from adapters.repositories.CityRepository import CityRepository
from adapters.repositories.MemberRepository import MemberRepository
from adapters.repositories.ReservationRepository import ReservationRepository
from bootstrap import bootstrap
from config import FastApi_metadata, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from events import commands, events
from events.commands import AddToMemberBalanceCommand, ReserveBookCommand, SetMemberVIPCommand
from events.events import OTPSendEvent
from events.requests import ReserveBookRequest
from helpers.json_web_token import create_jwt_token, get_current_member_id, JWTBearer
from messaging.rabbitMQ_broker import RabbitMQBroker
from services.OTPService import verify_otp
from services.RedisCacheService import set_redis_cache, delete_redis_cache
from services.UnitOfWork import UnitOfWork
from services.handlres import member_handler, otp_handler

logger = logging.getLogger(__name__)

msg_bus = bootstrap()

@asynccontextmanager
async def lifespan_context(app: FastAPI):
    rabbit = RabbitMQBroker()
    rabbit.declare_queue('otp_request')
    threading.Thread(
        target=lambda: rabbit.consume_messages(queue_name='otp_request', callback=handle_otp_request),
        daemon=True
    ).start()
    yield

    rabbit.close_connection()
    logger.info("rabbitMQ pubsub stopped")

def handle_otp_request(ch,method,properties,msg):
    data_str = msg.decode('utf-8')
    data_dict = json.loads(data_str)
    event = events.OTPSendEvent(data_dict.get("phone_number"))
    otp_handler.send_otp_handler(event)


app = FastAPI(lifespan=lifespan_context,openapi_tags=FastApi_metadata)

@app.get("/otp/get-code", tags=['Authorization'])
def generate_otp_code(phone_number: str):
    try:
        event = OTPSendEvent(phone_number)
        msg_bus.handle(event)
        return {"message": "Code Sent!"}
    except Exception as error:
        return {"error_message": str(error)}

@app.get("/otp/verify-code", tags=['Authorization'])
async def verify_otp_code(phone_number: str, code: str):
    try:
        result = verify_otp(phone_number, int(code))
        with UnitOfWork() as uow:
            member = member_handler.get_member_by_phone_number_handler(uow, phone_number)
            token = create_jwt_token({"UserData": jsonable_encoder(member)})

            # Cache the token in Redis with expiration
            await set_redis_cache(phone_number, token, JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        return {"Bearer": token}

    except Exception as error:
        return {"error_message": str(error)}


@app.get("/member/dismiss", tags=['Members'], dependencies=[Depends(JWTBearer())])
async def dismiss_member(phone_number: str):
    try:
        await delete_redis_cache(phone_number)
        return {"message": "Member Dismissed"}
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/cities", dependencies=[Depends(JWTBearer())])
def get_city_list():
    try:
        with UnitOfWork() as uow:
            repo = uow.get_repository(CityRepository)
            cities = repo.get_city_list()

            city_list = []
            for city in cities:
                city_data = {
                    "id": city.id,
                    "title": city.title
                }
                city_list.append(city_data)
            return {"cities": city_list}
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/authors", dependencies=[Depends(JWTBearer())])
def get_author_list():
    try:
        with UnitOfWork() as uow:
            repo = uow.get_repository(AuthorRepository)
            authors = repo.get_author_list()
            author_list = []
            for author in authors:
                city_data = {
                    "id": author.id,
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                    "city": {
                        "id": author.city.id,
                        "title": author.city.title
                    }
                }
                author_list.append(city_data)

            return {"authors": author_list}
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/books", tags=['Books'], dependencies=[Depends(JWTBearer())])
def get_book_list(
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        genres: Optional[str] = None,
        city_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by_price: str = 'asc'
):
    try:
        with UnitOfWork() as uow:
            repo = uow.get_repository(BookRepository)
            books = repo.get_book_list_filtered(
                search,
                min_price,
                max_price,
                genres,
                city_id,
                page,
                per_page,
                sort_by_price)
            return {"books": books}
    except Exception as error:
        return {"error_message": str(error)}


@app.post("/book", tags=['Books'], dependencies=[Depends(JWTBearer())])
def create_book(command: commands.CreateBookCommand):
    try:
        msg_bus.handle(command)
        return "Ok"
    except Exception as error:
        return {"error_message": str(error)}


@app.put("/book", tags=['Books'], dependencies=[Depends(JWTBearer())])
def update_book(command: commands.UpdateBookCommand):
    try:
        msg_bus.handle(command)
        return "Ok"
    except Exception as error:
        return {"error_message": str(error)}


@app.post("/member/deposit", tags=['Members'], dependencies=[Depends(JWTBearer())])
def add_to_balance(amount:int = Body(), token: str = Depends(JWTBearer())):
    try:
        member_id = get_current_member_id(token)
        command = AddToMemberBalanceCommand(member_id, amount)
        msg_bus.handle(command)
        return "Ok"
    except Exception as error:
        raise error
        return {"error_message": str(error)}




@app.post("/book/reserve", tags=['Books'], dependencies=[Depends(JWTBearer())])
def reserve_book(req:ReserveBookRequest, token: str = Depends(JWTBearer())):
    try:
        member_id = get_current_member_id(token)
        cmd = ReserveBookCommand(member_id, req.book_id,req.duration)
        msg_bus.handle(cmd)
        return "Ok"
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/member/reserved-books", tags=['Members'], dependencies=[Depends(JWTBearer())])
def get_reserved_books(token: str = Depends(JWTBearer())):
    try:
        with UnitOfWork() as uow:
            member_id = get_current_member_id(token)
            repo = uow.get_repository(ReservationRepository)
            books = repo.get_reserved_books(member_id)
            return {"books": books}
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/members", tags=['Members'], dependencies=[Depends(JWTBearer())])
def get_member_list():
    try:
        with UnitOfWork() as uow:
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
                    "membership_expiry": member.membership_expiry,
                    "balance": member.balance
                }

                result.append(member_data)

            return {"Members": result}
    except Exception as error:
        return {"error_message": str(error)}


@app.post("/member", tags=['Members'])
def create_member(command: commands.CreateMemberCommand):
    try:
        msg_bus.handle(command)
        return "Ok"
    except Exception as error:
        return {"error_message": str(error)}


@app.post("/member/set-vip", tags=['Members'], dependencies=[Depends(JWTBearer())])
def set_vip(token: str = Depends(JWTBearer())):
    try:
        member_id = get_current_member_id(token)
        cmd = SetMemberVIPCommand(member_id)
        msg_bus.handle(cmd)
        return "Ok"
    except Exception as error:
        return {"error_message": str(error)}
