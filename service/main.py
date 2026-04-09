import html
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response
from logging import getLogger, StreamHandler, Formatter, DEBUG
from logging.handlers import RotatingFileHandler
from .models import AzureTtsRequest, LogEntry, SyncFlowRuntimeSettings, AppSettings
from .syncflow_route import router as syncflow_router
from .admin_route import router as admin_router
from pathlib import Path

logger = getLogger("foodjustice-renpy-service")
logger.setLevel(DEBUG)
sh = StreamHandler()
formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setLevel(DEBUG)
sh.setFormatter(formatter)
logger.addHandler(sh)

Path("gamelogs").mkdir(parents=True, exist_ok=True)
rfh = RotatingFileHandler("gamelogs/service.log", maxBytes=1000000, backupCount=100)
rfh.setFormatter(formatter)
rfh.setLevel(DEBUG)
logger.addHandler(rfh)

logger.propagate = False
logger.info("Service started")


app = FastAPI()
app.include_router(syncflow_router, prefix="/syncflow")
app.include_router(admin_router, prefix="/admin")
settings = AppSettings()
app.state.syncflow_runtime_settings = SyncFlowRuntimeSettings(enabled=True)


@app.post("/player-log")
async def log_entry(entry: LogEntry):
    l = getLogger("foodjustice-renpy-service")
    l.info(
        f"Timestamp: {entry.timestamp} | User: {entry.user} | Action: {entry.action} | View: {entry.view} | Payload: {entry.payload}"
    )
    return {"status": "ok"}


def _build_azure_ssml(request: AzureTtsRequest) -> str:
    escaped_text = html.escape(request.utterance or "")
    safe_rate = str(request.rate or "0%")
    safe_style = str(request.style or "").strip()
    style_open = f'<mstts:express-as style="{html.escape(safe_style)}">' if safe_style else ""
    style_close = "</mstts:express-as>" if safe_style else ""
    safe_voice = html.escape(request.voice)
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">'
        f'<voice name="{safe_voice}">{style_open}<prosody rate="{html.escape(safe_rate)}">'
        f"{escaped_text}</prosody>{style_close}</voice></speak>"
    )


@app.post("/tts/azure")
async def azure_tts(request: AzureTtsRequest):
    tts_key = (settings.azure_tts_key or "").strip()
    if not tts_key:
        raise HTTPException(status_code=503, detail="Azure TTS is not configured")

    region = (settings.azure_tts_region or "eastus").strip()
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    payload = _build_azure_ssml(request).encode("utf-8")

    upstream = UrlRequest(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/ssml+xml",
            "Ocp-Apim-Subscription-Key": tts_key,
            "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3",
        },
    )

    try:
        with urlopen(upstream, timeout=15) as response:
            return Response(
                content=response.read(),
                media_type="audio/mpeg",
                headers={"Cache-Control": "no-store"},
            )
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") or str(exc)
        raise HTTPException(status_code=exc.code, detail=detail) from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"Azure TTS request failed: {exc.reason}") from exc


if settings.game_root_dir is not None:
    app.mount(
        "/", StaticFiles(directory=settings.game_root_dir, html=True), name="game"
    )

if settings.admin_build_dir is not None:

    @app.middleware("http")
    async def serve_static_file(request: Request, call_next):
        if not request.url.path.startswith("/control"):
            return await call_next(request)

        path = request.url.path.replace("/control", "")

        if path == "/" or path == "":
            path = "index.html"
            with open(f"{settings.admin_build_dir}/index.html") as f:
                return HTMLResponse(f.read())
        else:
            if path.startswith("/"):
                path = path[1:]

            pth: Path = Path(settings.admin_build_dir) / path

            if (
                pth.exists()
                or (
                    pth := Path(settings.admin_build_dir)
                    / f"{path.replace('/', '')}.html"
                ).exists()
            ):
                return FileResponse(pth)
            else:
                return Response(
                    status_code=404,
                    content=f"{request.url.path} not found",
                )
