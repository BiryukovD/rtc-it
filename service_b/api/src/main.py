from contextlib import asynccontextmanager

from aio_pika import connect_robust
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from mongodb import mongo
from rabbitmq import rabbit
from router import router as task_router
from config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        mongo.client = AsyncIOMotorClient(config.mongo.URI)
        mongo.db = mongo.client[config.mongo.DATABASE]
        mongo.collection = mongo.db[config.mongo.COLLECTION]
    except Exception as exc:
        raise RuntimeError(f"Cannot connect to MongoDB: {exc}")

    try:
        rabbit.connection = await connect_robust(config.rabbit.URI)
        rabbit.channel = await rabbit.connection.channel(publisher_confirms=True)
        rabbit.queue = await rabbit.channel.declare_queue(config.rabbit.QUEUE_NAME, durable=config.rabbit.DURABLE)
    except Exception as exc:
        raise RuntimeError(f"Cannot connect to RabbitMQ: {exc}")

    yield
    mongo.client.close()
    await rabbit.channel.close()
    await rabbit.connection.close()

app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal provisioning exception"
        }
    )

app.include_router(task_router)
