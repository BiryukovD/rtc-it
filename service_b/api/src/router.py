import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo


from aio_pika import DeliveryMode, Message
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse

from dependencies import get_mongo, get_rabbit
from mongodb import MongoDB
from rabbitmq import RabbitMQ
from shemas import Config


logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["tasks"])


@router.post('/api/v1/equipment/cpe/{id}')
async def configuring_equipment(config: Config,
                                rabbit: RabbitMQ = Depends(get_rabbit),
                                id: str = Path(..., regex="^[a-zA-Z0-9]{6,}$"),
                                mongo: MongoDB = Depends(get_mongo)
                                ):
    try:
        timestamp = datetime.now(ZoneInfo("Europe/Moscow"))
        result = {
            'code': 204,
            'message': 'Task is still running'
        }
        result = await mongo.collection.insert_one({"timestamp": timestamp, "equipment_id": id, "parameter": config.model_dump(), "status": "processing", "result": result})
        task_id = str(result.inserted_id)
        logger.info("Created task %s for equipment %s", task_id, id)

        message_data = {"task_id": task_id,
                        "equipment_id": id, "config": config.model_dump()}
        message_body = json.dumps(message_data).encode()
        message = Message(message_body,
                          delivery_mode=DeliveryMode.PERSISTENT
                          )
        await rabbit.channel.default_exchange.publish(
            message,
            routing_key=rabbit.queue.name
        )
        logger.info(
            "Published task %s to RabbitMQ queue '%s'",
            task_id, rabbit.queue.name
        )
    except Exception as exc:
        logger.exception("Task creation failed for equipment %s", id)
        raise HTTPException(
            status_code=500, detail=f"Task creation failed: {str(exc)}")
    return {"code": 200, "taskId": task_id}


@router.get('/api/v1/equipment/cpe/{id}/task/{task_id}')
async def configuring_equipment(
        task_id: str = Path(..., regex=r"^[0-9a-f]{24}$"),
        id: str = Path(..., regex="^[a-zA-Z0-9]{6,}$"),
        mongo: MongoDB = Depends(get_mongo)):

    oid = ObjectId(task_id)
    task = await mongo.collection.find_one({"_id": oid, "equipment_id": id})
    if not task:
        logger.warning(
            "Task not found: task_id=%s, equipment_id=%s", task_id, id)
        data = {
            'code': 404,
            'message': 'The requested task is not found'}
        return JSONResponse(content=data, status_code=404)

    task["_id"] = str(task["_id"])
    result = task.get("result") or {}
    return JSONResponse(content=result, status_code=200)
