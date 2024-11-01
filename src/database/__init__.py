import asyncio
import io
from sqlmodel import create_engine, Session
import redis as redis_py

from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)

# redis
redis_url = settings.redis_url
user_redis = redis_py.Redis.from_url(redis_url + "/1")
redis = redis_py.Redis.from_url(redis_url + "/0")


def get_db():
    db = Session(engine)
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_user_redis():
    return user_redis


def get_redis():
    return redis
