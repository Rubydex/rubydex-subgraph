import redis
import redis.asyncio as redis_async
from config import REDIS_CONFIG


def get_redis_connection():
    return redis.Redis(**REDIS_CONFIG)

def get_redis_async_connection():
    return redis_async.Redis(**REDIS_CONFIG)
