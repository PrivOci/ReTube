import json
import redis
import sys
from datetime import timedelta
import socket

DISABLE_CACHE = False


def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def redis_connect() -> redis.client.Redis:
    host = "localhost" if isOpen("localhost", 6379) else "redis"
    try:
        client = redis.Redis(
            host=host,
            port=6379,
            password="retube",
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)


client = redis_connect()


def set_cache(key: str, value: str, hours = 24) -> bool:
    """Data to redis - 1 hour"""

    state = client.setex(key, timedelta(hours=hours), value=value,)
    return state

async def get_from_cache(key: str) -> str:
    """Data from redis."""

    val = client.get(key)
    return val


async def optimized_request(details, get_from_source, hours=24, forced=False):

    key_for_redis = json.dumps(details)
    # First it looks for the data in redis cache
    data = await get_from_cache(key_for_redis) if not DISABLE_CACHE else None

    # If cache is found then serves the data from cache
    if data is not None and forced is False:
        data = json.loads(data)
        data["cache"] = True
        return data

    else:
        # If cache is not found then sends request to the MapBox API
        data = await get_from_source(details)
        if not data:
            return {
                "ready": "False"
            }

        # This block sets saves the respose to redis and serves it directly
        if data.get("ready") == True:
            data["cache"] = False
            state = set_cache(key_for_redis, json.dumps(data), hours)

            if state is True:
                return data
        return data
