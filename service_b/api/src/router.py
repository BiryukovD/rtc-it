import json

from aio_pika import DeliveryMode, Message
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path

from dependencies import get_mongo, get_rabbit
from mongodb import MongoDB
from rabbitmq import RabbitMQ
from shemas import Config

router = APIRouter(prefix="", tags=["tasks"])

@router.post('/api/v1/equipment/cpe/{id}')
async def configuring_equipment(config: Config,
                                rabbit: RabbitMQ = Depends(get_rabbit),
                                id: str = Path(..., regex="^[a-zA-Z0-9]{6,}$"),
                                mongo: MongoDB = Depends(get_mongo)
                                ):
    try:
        result = await mongo.collection.insert_one({"equipment_id": id, "config": config.model_dump(), "status": "pending", "result": {}})
        task_id = str(result.inserted_id)

        message_data = {"task_id": task_id, "config": config.model_dump()}
        message_body = json.dumps(message_data).encode()
        message = Message(message_body,
                        delivery_mode=DeliveryMode.PERSISTENT
                        )
        await rabbit.channel.default_exchange.publish(
            message,
            routing_key=rabbit.queue.name
        )
    except Exception as exc:
          raise HTTPException(status_code=500, detail=f"Task creation failed: {str(exc)}")
    return {"task_id": task_id}

@router.get('/api/v1/equipment/cpe/{id}/task/{task_id}')
async def configuring_equipment(
        task_id: str,
        id: str = Path(..., regex="^[a-zA-Z0-9]{6,}$"),
        mongo: MongoDB = Depends(get_mongo)):

    try:
        oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    task = await mongo.collection.find_one({"_id": oid, "equipment_id": id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task["_id"] = str(task["_id"])
    return task
