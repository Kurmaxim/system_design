import redis


REDIS_URL = "redis://cache:6379/0"
redis_client = redis.from_url(REDIS_URL)

try:
    redis_client.ping()
    print("Redis is working!")
except Exception as e:
    print(f"Redis connection error: {e}")