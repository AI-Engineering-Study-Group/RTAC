# app/services/cache.py
import redis
from app.config.settings import settings


redis_client = None

def init_cache():
    global redis_client
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True
    )

def set_cache(key, value, expire_seconds=3600):
    redis_client.set(key, value, ex=expire_seconds)

def get_cache(key):
    return redis_client.get(key)

def delete_cache(key):
    redis_client.delete(key)
