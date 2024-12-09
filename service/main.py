import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from pydantic import BaseModel
from logging import getLogger, StreamHandler, Formatter, DEBUG
from logging.handlers import RotatingFileHandler

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


class LogEntry(BaseModel):
    action: str
    timestamp: str
    user: str
    view: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


app = FastAPI()


@app.post("/player-log")
async def log_entry(entry: LogEntry):
    l = getLogger("foodjustice-renpy-service")
    l.info(
        f"Timestamp: {entry.timestamp} | User: {entry.user} | Action: {entry.action} | View: {entry.view} | Payload: {entry.payload}"
    )
    return {"status": "ok"}


if os.getenv("GAME_ROOT_DIR") is not None:
    print(f"GAME_ROOT_DIR: {os.getenv('GAME_ROOT_DIR')}")
    app.mount(
        "/", StaticFiles(directory=os.getenv("GAME_ROOT_DIR"), html=True), name="game"
    )
