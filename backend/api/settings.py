import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    URI = "mongodb://mongodb:27017/"

    if os.getenv("NODE_ENV") == "production":
        MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD")

        URI = f"mongodb://root:{MONGO_ROOT_PASSWORD}@mongodb:27017/"

    MONGO_URI: str = URI


settings = Settings()
