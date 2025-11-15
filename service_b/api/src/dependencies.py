from mongodb import mongo
from rabbitmq import rabbit


async def get_rabbit():
    return rabbit

async def get_mongo():
    return mongo
