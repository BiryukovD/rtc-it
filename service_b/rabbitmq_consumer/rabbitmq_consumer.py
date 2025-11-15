import asyncio
import aio_pika
import json
from config import config
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def main():
    connection = await aio_pika.connect_robust(
        config.rabbit.URI
    )

    mongo_client = AsyncIOMotorClient(config.mongo.URI)
    mongo_db = mongo_client[config.mongo.DATABASE]
    mongo_collection = mongo_db[config.mongo.COLLECTION]

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

                        print(type(body_data))
                        print(body_data)

                        task_id = body_data.get("task_id")
                        oid = ObjectId(task_id)
                        task = await mongo_collection.find_one({"_id": oid})

                        if task:
                            result = body_data.get('result')    
                            await mongo_collection.insert_one({"status": "сompleted", "result": result})

                    except Exception as exc:
                        print(exc)


if __name__ == "__main__":
    asyncio.run(main())