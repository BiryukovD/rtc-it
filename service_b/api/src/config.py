from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

import os
import pprint

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

class MongoDB(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="MONGODB_")
    URI: str = Field(default="mongodb://admin:secret@localhost:27017")
    DATABASE: str = Field(default="test_database")
    COLLECTION: str = Field(default="test_collection")

class RabbitMQ(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")
    URI: str = Field(default="amqp://guest:guest@localhost:5672/")
    TASK_QUEUE_NAME: str = Field(default="tasks")
    DURABLE: bool = Field(default=True)


class Config(BaseSettings):
    mongo: MongoDB = Field(default_factory=MongoDB)
    rabbit: RabbitMQ = Field(default_factory=RabbitMQ)

    @classmethod
    def load(cls) -> "Config":
        return cls()
    
    def show(self):
        """Вывод всех переменных окружения конфигурации"""
        pprint.pprint({
            "mongo": self.mongo.model_dump(),
            "rabbit": self.rabbit.model_dump()
        }, width=120)
    
config = Config.load()
# Вывод всех переменных
config.show()