from contextlib import asynccontextmanager
import logging
import time
from beanie import init_beanie
from fastapi import FastAPI, Response
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import motor
import motor.motor_asyncio
from sqlmodel import SQLModel

# region 初始化数据库Activated
from config import get_settings
from database import engine, mongodb_models

SQLModel.metadata.create_all(engine)
# endregion

@asynccontextmanager
async def live_span(_: FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(get_settings().mongo_url)
    await init_beanie(database=client.goodstuff, document_models=mongodb_models.models)
    yield


app = FastAPI(lifespan=live_span)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


from router import router

app.include_router(router)
