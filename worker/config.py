import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", extra="ignore"
    )

class RabbitMQ(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")
    URI: str = Field(default="amqp://guest:guest@localhost:5672/")
    RESULT_QUEUE_NAME: str = Field(default="results")
    TASK_QUEUE_NAME: str = Field(default="tasks")
    DURABLE: bool = Field(default=True)

class ServiceA(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="SERVICEA_")
    BASE_URL: str = Field(default="http://localhost:8002")
    TIMEOUT: int = Field(default=120)



class Config(BaseSettings):
    rabbit: RabbitMQ = Field(default_factory=RabbitMQ)
    service_a: ServiceA = Field(default_factory=ServiceA)

    @classmethod
    def load(cls) -> "Config":
        return cls()
    
config = Config.load()
