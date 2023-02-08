from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://mongodb:27017/"


settings = Settings()
