from bcrypt import checkpw
from .models import Claims
import jwt
from time import time


def is_valid_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode(), hashed_password.encode())


def is_valid_token(token: str, secret: str) -> bool:
    try:
        claims = Claims.model_validate(jwt.decode(token, secret, algorithms=["HS256"]))
        return claims.exp > time()
    except:
        return False
