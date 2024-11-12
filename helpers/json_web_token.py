from datetime import datetime, timedelta
import redis.asyncio as redis
import jwt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration settings (make sure these are defined in config)
from config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY, JWT_ALGORITHM
from services.RedisCacheService import get_redis_cache

# Initialize Redis connection
redis = redis.from_url("redis://localhost:6379", decode_responses=True)

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        data = get_current_user(credentials.credentials)
        token_status = await get_redis_cache(data["phone_number"])
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not await self.verify_jwt(credentials.credentials) or not token_status:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    async def verify_jwt(self, jwt_token: str) -> bool:
        try:
            payload = jwt_decode(jwt_token)
            return True
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token expired.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=403, detail="Invalid token.")

def get_current_user(token: str):
    user_data = jwt_decode(token)
    return user_data.get("UserData")

def get_current_member_id(token: str) -> int:
    user_data = get_current_user(token)
    return int(user_data.get("id"))

def jwt_decode(token: str):
    # Decode the token with proper algorithm listing
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
