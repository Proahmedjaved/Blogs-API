import json
from redis import Redis
from app.core.config import settings

redis_client = Redis.from_url(settings.REDIS_URL)

def get_cache(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key: str, value, expiry: int = 3600):
    redis_client.setex(key, expiry, json.dumps(value))

def invalidate_cache(key: str):
    redis_client.delete(key)

def invalidate_pattern(pattern: str):
    for key in redis_client.keys(pattern):
        redis_client.delete(key) 