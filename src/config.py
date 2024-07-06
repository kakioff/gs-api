from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    temp_dir: str = "./tmp/"
    database_url: str
    secret_key: str
    cos_secret_id: str
    cos_secret_key: str
    cos_bucket: str
    cos_region: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings() # type: ignore
