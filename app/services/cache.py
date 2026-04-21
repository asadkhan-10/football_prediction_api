
import redis
import json
from app.config import settings

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

def get_cached(key: str):
    data = redis_client.get(key) # type: ignore
    if data:
        return json.loads(data)
    return None

def set_cached(key: str, value: dict, ttl_seconds: int = 300):
    redis_client.setex(key, ttl_seconds, json.dumps(value))#type: ignore

def delete_cached(key: str):
    redis_client.delete(key)#type: ignore