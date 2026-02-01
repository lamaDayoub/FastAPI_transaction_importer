import os
import redis.asyncio as redis

# Inside Docker, the hostname is 'redis' (from your docker-compose)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Setup the async connection
# decode_responses=True means we get back Strings instead of Bytes
redis_client = redis.from_url(REDIS_URL, decode_responses=True)