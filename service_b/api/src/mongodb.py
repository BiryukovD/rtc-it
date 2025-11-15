from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    client: AsyncIOMotorClient | None = None
    db = None
    collection = None

mongo = MongoDB()
