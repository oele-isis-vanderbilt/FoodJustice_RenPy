import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

print(f"GAME_ROOT_DIR: {os.getenv('GAME_ROOT_DIR')}")

if os.getenv("GAME_ROOT_DIR") is not None:
    print(f"GAME_ROOT_DIR: {os.getenv('GAME_ROOT_DIR')}")
    app.mount(
        "/", StaticFiles(directory=os.getenv("GAME_ROOT_DIR"), html=True), name="game"
    )


@app.get("/message")
async def read_root():
    return {"Hello": "World"}
