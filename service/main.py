import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response
from logging import getLogger, StreamHandler, Formatter, DEBUG
from logging.handlers import RotatingFileHandler
from .models import LogEntry, SyncFlowRuntimeSettings, AppSettings
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
