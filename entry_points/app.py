from typing import Optional
import redis.asyncio as redis
from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URL, FastApi_metadata, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from domains.adapters import table_mapping
from events import events, commands
from events.commands import AddToMemberBalanceCommand
from exceptions.BaseException import MemberDoesNotExistError
from helpers.json_web_token import create_jwt_token, get_current_member_id, JWTBearer

from services import CityService, AuthorService, BookService, MemberService
from services.MemberService import get_member_by_phone_number_service, add_to_balance_service, set_to_vip_service
from services.OTPService import generate_otp, verify_otp
from services.ReservationService import reserve_service, get_reserved_books_service
from services.UnitOfWork import UnitOfWork

app = FastAPI(openapi_tags=FastApi_metadata)

# Initialize Redis connection
redis = redis.from_url("redis://localhost:6379", decode_responses=True)

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
table_mapping.start_mappers()

@app.get("/OTPService/get_code",tags=['Authorization'])
def generate_otp_code(phone_number:str):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member = get_member_by_phone_number_service(uow,phone_number)
                if not member:
                    raise MemberDoesNotExistError()

                code = generate_otp(phone_number)
                print(f"OTP Verification Code: {code}")
                return {"message": "Code Retrieved Successfully!"}
    except Exception as error:
        return {"error_message": str(error)}

@app.get("/OTPService/verify_code",tags=['Authorization'])
async def verify_otp_code(phone_number:str,code:str):
    try:
        result = verify_otp(phone_number,int(code))
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member = get_member_by_phone_number_service(uow,phone_number)
                token = create_jwt_token({"UserData":jsonable_encoder(member)})

                # Cache the token in Redis with expiration
                await redis.setex(phone_number, JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,token)

                return {"Bearer":token}
    except Exception as error:
        return {"error_message": str(error)}

@app.get("/Member/Dismiss")
async def dismiss_member(phone_number:str):
    try:
        await redis.delete(phone_number)
        return {"message": "Member Dismissed"}
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/City/get_list", dependencies=[Depends(JWTBearer())])
def get_city_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                city_list = CityService.get_city_list_service(uow)
                return {"cities": city_list}
    except Exception as error:
        return {"error_message": str(error)}

@app.get("/Author/get_list", dependencies=[Depends(JWTBearer())])
def get_author_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                author_list = AuthorService.get_author_list_service(uow)
                return {"authors": author_list}
    except Exception as error:
        return {"error_message": str(error)}

@app.get("/books/get_list",tags=['Books'], dependencies=[Depends(JWTBearer())])
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
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                event = events.SearchBooksEvent(search, min_price, max_price, genres, city_id, page, per_page, sort_by_price)
                books = BookService.get_book_list_filtered_service(uow, event)
                return {"books": books}
    except Exception as error:
        return {"error_message": str(error)}

@app.post("/books", response_model=commands.CreateBookCommand, tags=['Books'], dependencies=[Depends(JWTBearer())])
def create_book(command: commands.CreateBookCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                BookService.add_book_service(uow,command)
                return command
    except Exception as error:
        return {"error_message": str(error)}


@app.post("/Members/Deposit",tags=['Members'], dependencies=[Depends(JWTBearer())])
def add_to_balance(command:AddToMemberBalanceCommand,token:str = Depends(JWTBearer())):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member_id = get_current_member_id(token)
                add_to_balance_service(uow,member_id, command)
                return {"message": "Balance Updated Successfully!"}
    except Exception as error:
        return {"error_message": str(error)}

@app.post("/Books/Reserve",tags=['Books'], dependencies=[Depends(JWTBearer())])
def reserve_book(cmd: commands.ReserveBookCommand,token:str = Depends(JWTBearer())):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member_id = get_current_member_id(token)
                reserved_book = reserve_service(uow, cmd,member_id)
                return {"message": "Book is reserved successfully , enjoy"}
    except Exception as error:
        return {"error_message": str(error)}

@app.get("/Members/get_reserved_books",tags=['Members'], dependencies=[Depends(JWTBearer())])
def get_reserved_books(token:str = Depends(JWTBearer())):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member_id = get_current_member_id(token)
                books = get_reserved_books_service(uow, member_id)
                return {"books": books}
    except Exception as error:
        return {"error_message": str(error)}


@app.get("/Members/get_list",tags=['Members'], dependencies=[Depends(JWTBearer())])
def get_member_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                members = MemberService.get_members_service(uow)
                return members
    except Exception as error:
        return {"error_message": str(error)}

@app.post("/Members",tags=['Members'], dependencies=[Depends(JWTBearer())])
def create_member(command: commands.CreateMemberCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                MemberService.add_member_service(uow, command)
                return command
    except Exception as error:
        return {"error_message": str(error)}

@app.post("/Members/SetVIP",tags=['Members'], dependencies=[Depends(JWTBearer())])
def set_vip(token:str = Depends(JWTBearer())):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member_id = get_current_member_id(token)
                set_to_vip_service(uow,member_id)
                return {"message":"You are now a Premium Member , enjoy your life"}
    except Exception as error:
        return {"error_message": str(error)}
