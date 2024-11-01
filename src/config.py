from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    temp_dir: str = "./tmp/"
    database_url: str
    mongo_url: str
    redis_url: str
    secret_key: str
    cos_secret_id: str
    cos_secret_key: str
    cos_bucket: str
    cos_region: str
    pexel_api_key: str

    mail_smtp_server: str
    mail_smtp_port: int
    mail_imap_server: str
    mail_imap_port: int
    mail_nick_name: str
    mail_username: str
    mail_password: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings() # type: ignore
