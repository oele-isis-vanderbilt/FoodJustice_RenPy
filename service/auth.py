from bcrypt import checkpw, hashpw, gensalt
from .models import Claims
import jwt
from time import time


def is_valid_password(password: str, plain_pw: str) -> bool:
    hashed_password = hashpw(plain_pw.encode(), gensalt(12))
    return checkpw(password.encode(), hashed_password=hashed_password)


def is_valid_token(token: str, secret: str) -> bool:
    try:
        claims = Claims.model_validate(jwt.decode(token, secret, algorithms=["HS256"]))
        return claims.exp > time()
    except:
        return False
