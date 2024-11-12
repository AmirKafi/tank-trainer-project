import os

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:admin@localhost/Booking_DB"

MEMBER_PREMIUM_COST=1000
MEMBER_PREMIUM_Period_Month= 1

RESERVATION_COST_PER_DAY = 1000
RESERVATION_MINIMUM_PAYMENT_FOR_DISCOUNT = 300000
RESERVATION_MINIMUM_BOOKS_COUNT_FOR_DISCOUNT = 300000

OTP_EXPIRY_MINUTES = 5
OTP_REQUEST_LIMIT_PER_2_MINUTES = 5
OTP_REQUEST_LIMIT_PER_HOUR = 10

JWT_SECRET_KEY = "this-is-my-secret-key-yoyo"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 63791 if host == "localhost" else 6379
    return dict(host=host, port=port)

FastApi_metadata = [
    {
        "name": "Books",
        "description": "Operations with books. Creation and filtered list",
    },
    {
        "name": "Members",
        "description": "Managing Members ,submission VIP purchase"
    },
    {
        "name": "Authorization",
        "description":"OTP services , and login"
    }
]
