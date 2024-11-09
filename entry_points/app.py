import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domains.adapters import table_mapping
from events import events, commands
from events import AddToMemberBalanceCommand
from exceptions.BaseException import MemberDoesNotExistError
from services import CityService, AuthorService, BookService, MemberService
from services.MemberService import get_member_by_phone_number_service, add_to_balance_service, set_to_vip_service
from services.OTPService import generate_otp, verify_otp
from services.ReservationService import reserve_service, get_reserved_books_service

from services.UnitOfWork import UnitOfWork
from config import SQLALCHEMY_DATABASE_URL, FastApi_metadata, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, \
    JWT_SECRET_KEY

app = FastAPI(openapi_tags=FastApi_metadata)

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

table_mapping.start_mappers()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger = logging.getLogger("uvicorn.error")  # FastAPI integrates well with uvicorn logging
logger.setLevel(logging.DEBUG)

class Token(BaseModel):
    access_token: str
    token_type: str

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
        return {"message": str(error)}

@app.get("/OTPService/verify_code",tags=['Authorization'])
def verify_otp_code(phone_number:str,code:str):
    try:
        result = verify_otp(phone_number,int(code))
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                member = get_member_by_phone_number_service(uow,phone_number)
                token = create_jwt_token({"UserData":jsonable_encoder(member)})
                return "bearer " + token
    except Exception as error:
        return {"message": str(error)}

@app.get("/City/get_list")
def get_city_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                city_list = CityService.get_city_list_service(uow)
                return {"cities": city_list}
    except Exception as e:
        logger.error(f"Error retrieving Cities: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving Cities {e}")

@app.get("/Author/get_list")
def get_author_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                author_list = AuthorService.get_author_list_service(uow)
                return {"authors": author_list}
    except Exception as e:
        logger.debug(f"Error retrieving authors: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving authors")

@app.get("/books/get_list",tags=['Books'])
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
    except Exception as e:
        logger.debug(f"Error retrieving books: {e}")

@app.post("/books", response_model=commands.CreateBookCommand, tags=['Books'])
def create_book(command: commands.CreateBookCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                BookService.add_book_service(uow,command)
                return command
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        raise HTTPException(status_code=500, detail="Error creating book")


@app.post("/Members/Deposit",tags=['Members'])
def add_to_balance(command:AddToMemberBalanceCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                add_to_balance_service(uow, command)
                return {"message": "Balance Updated Successfully!"}
    except Exception as error:
        return {"message": str(error)}

@app.post("/Books/Reserve",tags=['Books'])
def reserve_book(cmd: commands.ReserveBookCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                reserved_book = reserve_service(uow, cmd)
                return {"message": "Book is reserved successfully , enjoy"}
    except Exception as error:
        return {"error_message":str(error)}

@app.get("/Members/get_reserved_books",tags=['Members'])
def get_reserved_books(member_id:int):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                books = get_reserved_books_service(uow, member_id)
                return {"books": books}
    except Exception as e:
        return {"error_message":str(e)}


@app.get("/Members/get_list",tags=['Members'])
def get_member_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                members = MemberService.get_members_service(uow)
                return members
    except Exception as e:
        logger.debug(f"Error retrieving members: {e}")

@app.post("/Members",tags=['Members'])
def create_member(command: commands.CreateMemberCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                MemberService.add_member_service(uow, command)
                return command
    except Exception as e:
        logger.error(f"Error creating Member: {e}")
        raise HTTPException(status_code=500, detail="Error creating Member")

@app.post("/Members/SetVIP",tags=['Members'])
def set_vip(command: commands.SetVIPMemberCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                set_to_vip_service(uow,command)
                return {"message":"You are now a Premium Member , enjoy your life"}
    except Exception as e:
        logger.error(f"Error setting VIP: {e}")
        return {"message": str(e)}

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
