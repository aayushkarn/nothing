from datetime import timedelta,datetime, timezone
import jwt
from pydantic import BaseModel

import config

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

def create_access_token(data:dict):
    expiration_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    expiration = datetime.now(timezone.utc)+expiration_delta
    to_encode = data.copy()
    to_encode.update({"exp":expiration})

    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data:dict):
    expiration_delta = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    expiration = datetime.now(timezone.utc)+expiration_delta
    to_encode = data.copy()
    to_encode.update({"exp":expiration})

    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt