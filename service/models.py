from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.alias_generators import to_camel
import jwt


class AppSettings(BaseSettings):
    root_user: str
    root_password: str
    game_root_dir: Optional[str] = None
    admin_build_dir: Optional[str] = None
    jwt_secret: str

    model_config = SettingsConfigDict(
        env_file=".env.app",
    )


class LogEntry(BaseModel):
    action: str
    timestamp: str
    user: str
    view: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class SyncflowSettings(BaseSettings):
    syncflow_server_url: str
    syncflow_project_id: str
    syncflow_api_key: str
    syncflow_api_secret: str

    model_config = SettingsConfigDict(
        env_file=".env.syncflow",
    )


class SyncFlowRuntimeSettings(BaseModel):
    enabled: bool
    session_name: Optional[str] = None
    enable_camera: bool = False
    enable_audio: bool = False
    enable_screen_share: bool = False

    model_config = ConfigDict(alias_generator=to_camel)


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class Claims(BaseModel):
    username: str
    exp: int
    iat: int

    def to_jwt(self, secret: str) -> str:
        return jwt.encode(self.model_dump(), secret, algorithm="HS256")
