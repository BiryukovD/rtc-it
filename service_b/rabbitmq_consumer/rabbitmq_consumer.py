import asyncio
import aio_pika
import json
from config import config
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging
import time


from config import config
from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def main():
    time.sleep(10)
    try:
        connection = await aio_pika.connect_robust(
            config.rabbit.URI
        )
    except Exception as exc:
        logger.exception(f"Failed to connect to RabbitMQ: {exc}")
        return

    try:
        mongo_client = AsyncIOMotorClient(config.mongo.URI)
        mongo_db = mongo_client[config.mongo.DATABASE]
        mongo_collection = mongo_db[config.mongo.COLLECTION]
    except Exception as exc:
        logger.exception(f"Failed to connect to MongoDB: {exc}")
        return
    
    async with connection:
        queue_name = config.rabbit.RESULT_QUEUE_NAME
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=config.rabbit.DURABLE)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        body_bytes = message.body
                        body_str = body_bytes.decode("utf-8")
                        body_data = json.loads(body_str)

                        logger.info(
                            "Received result for task_id %s from queue '%s'",
                            body_data.get("task_id"),
                            queue_name
                        )

                        task_id = body_data.get("task_id")
                        oid = ObjectId(task_id)
                        task = await mongo_collection.find_one({"_id": oid})

                        if task:
                            result = body_data.get("result")
                            status_code = result.get("code")
                            if status_code == 200:
                                result["message"] = "Completed"
                            await mongo_collection.update_one(
                                {"_id": oid},
                                {"$set": {"status": "completed", "result": result}}
                            )
                            logger.info(
                                "Result for task_id %s successfully updated: %s",
                                task_id,
                                result
                            )
                    except Exception as exc:
                        logger.exception(
                            f"Failed to connect to MongoDB: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
