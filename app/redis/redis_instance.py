# app/redis/redis_instance.py
import redis

# Configure Redis connection
redis_client = redis.Redis(host="redis", port=6379, db=2)


# Expose the Redis client instance
def get_redis_client():
    return redis_client
