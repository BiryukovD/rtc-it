import asyncio
import json
import logging
import ssl
from urllib.parse import urlparse
import time

import aio_pika
import aiohttp
from aio_pika import Message
import logging

from config import config
from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
timeout = aiohttp.ClientTimeout(total=config.service_a.TIMEOUT)


async def main(loop):
    time.sleep(10)
    try:
        logger.info(f"Connecting to RabbitMQ: {config.rabbit.URI}")
        connection = await aio_pika.connect_robust(config.rabbit.URI, loop=loop)
        logger.info("Connected to RabbitMQ")
    except Exception as exc:
        logger.exception(f"Failed to connect to RabbitMQ: {exc}")
        

    async with connection:
        channel = await connection.channel()
        tasks_queue = await channel.declare_queue(config.rabbit.TASK_QUEUE_NAME, durable=config.rabbit.DURABLE)
        result_queue = await channel.declare_queue(config.rabbit.RESULT_QUEUE_NAME, durable=config.rabbit.DURABLE)

        async with tasks_queue.iterator() as queue_iter:
            while True:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            body_bytes = message.body
                            body_str = body_bytes.decode("utf-8")
                            body_data = json.loads(body_str)

                            config_equipment = body_data.get("config")
                            task_id = body_data.get("task_id")
                            equipment_id = body_data.get("equipment_id")

                            logger.info(
                                f"Processing task_id={task_id}, equipment_id={equipment_id}")

                            parsed = urlparse(config.service_a.BASE_URL)
                            ssl_context = None
                            if parsed.scheme == "https":
                                ssl_context = ssl.create_default_context() 
                            async with aiohttp.ClientSession(timeout=timeout) as session:
                                async with session.post(f"{config.service_a.BASE_URL}/api/v1/equipment/cpe/{equipment_id}", json=config_equipment, ssl=ssl_context) as resp:
                                    result = await resp.json()

                        except Exception as exc:
                            logger.exception(exc)
                            result = {
                                "code": 500,
                                "message": "Internal provisioning exception"
                            }

                        try:
                            response_message = {"task_id": task_id, "result": result}
                            logger.info(response_message)
                            await channel.default_exchange.publish(
                                Message(body=json.dumps(response_message).encode("utf-8")),
                                routing_key=result_queue.name
                            )
                            logger.info(f"Published result for task_id={task_id}")
                        except Exception as exc:
                            logger.exception(f"Failed to publish result for task_id={task_id}: {exc}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
    # asyncio.run(main())
