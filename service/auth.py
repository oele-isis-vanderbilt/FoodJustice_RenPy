from bcrypt import checkpw
from .models import Claims
import jwt
from jwt import InvalidTokenError
from time import time


def is_valid_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False

    try:
        return checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def is_valid_token(token: str, secret: str) -> bool:
    try:
        claims = Claims.model_validate(jwt.decode(token, secret, algorithms=["HS256"]))
        return claims.exp > time()
    except (InvalidTokenError, ValueError, TypeError):
        return False
