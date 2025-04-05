from fastapi import APIRouter, Request, Depends, Header, HTTPException
from typing import Optional, Annotated
from .models import SyncFlowRuntimeSettings, SyncflowSettings, AppSettings
from syncflow.project_client import ProjectClient
from .auth import is_valid_token

from syncflow.models import (
    TokenRequest,
    TokenResponse,
    CreateSessionRequest,
    VideoGrantsWrapper,
)

settings = SyncflowSettings()
app_settings = AppSettings()


def is_logged_in(request: Request):
    token = request.cookies.get("auth_token")
    if token is None:
        return False
    if not is_valid_token(token, app_settings.jwt_secret):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


router = APIRouter()
client = ProjectClient(
    api_key=settings.syncflow_api_key,
    api_secret=settings.syncflow_api_secret,
    project_id=settings.syncflow_project_id,
    server_url=settings.syncflow_server_url,
)


@router.get("/runtime-settings")
async def get_settings(request: Request) -> SyncFlowRuntimeSettings:
    settings = request.app.state.syncflow_runtime_settings
    return settings


@router.put("/runtime-settings", dependencies=[Depends(is_logged_in)])
async def update_settings(
    settings: SyncFlowRuntimeSettings, request: Request
) -> SyncFlowRuntimeSettings:
    request.app.state.syncflow_runtime_settings = settings
    return request.app.state.syncflow_runtime_settings


@router.get("/token", response_model=TokenResponse)
async def get_token(identity: str, request: Request) -> TokenResponse:
    settings = request.app.state.syncflow_runtime_settings

    sessions = await client.list_sessions()

    for session in sessions:
        if session.name == settings.session_name and session.status == "Started":
            return await client.generate_session_token(
                session_id=session.id,
                token_request=TokenRequest(
                    identity=identity,
                    video_grants=VideoGrantsWrapper(room=session.name),
                ),
            )

    new_session = await client.create_session(
        CreateSessionRequest(
            name=settings.session_name,
            max_participants=100,
            auto_recording=True,
        )
    )

    return await client.generate_session_token(
        session_id=new_session.id,
        token_request=TokenRequest(
            identity=identity, video_grants=VideoGrantsWrapper(room=new_session.name)
        ),
    )
