from fastapi import APIRouter, Request, Response, HTTPException
from .models import AdminLoginRequest, AppSettings, Claims
from .auth import is_valid_password, is_valid_token
import time

router = APIRouter()


@router.post("/login")
async def login(login_request: AdminLoginRequest, response: Response):
    settings = AppSettings()
    if login_request.username == settings.root_user and is_valid_password(
        login_request.password, settings.root_password
    ):
        claims = Claims(
            username=login_request.username,
            iat=int(time.time()),
            exp=int(time.time() + 3600 * 24),
        )
        token = claims.to_jwt(settings.jwt_secret)
        response.set_cookie(key="auth_token", value=token, httponly=True, expires=3600)
        return {"status": "ok"}
    else:
        response.status_code = 401
        return {"status": "unauthorized"}


@router.get("/is-logged-in")
async def is_logged_in(request: Request):
    settings = AppSettings()
    token = request.cookies.get("auth_token")
    if token is None:
        return {"loggedIn": False}
    if not is_valid_token(token, settings.jwt_secret):
        return {"loggedIn": False}
    return {"loggedIn": True}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"status": "ok"}
