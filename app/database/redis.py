import redis.asyncio as redis
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import config

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client for caching and other operations.
    """

    def __init__(self):
        self.redis_url = config.REDIS_URL
        self.client = None

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    async def connect(self):
        """
        Connect to Redis with retry logic.
        """
        if self.client is None:
            try:
                self.client = redis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                await self.client.ping()
                logger.info("Successfully connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise e
        return self.client

    async def get(self, key: str):
        """
        Get a value from Redis.
        """
        client = await self.connect()
        return await client.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        """
        Set a value in Redis with optional expiration.
        """
        client = await self.connect()
        await client.set(key, value)
        if expire:
            await client.expire(key, expire)

    async def delete(self, key: str):
        """
        Delete a key from Redis.
        """
        client = await self.connect()
        await client.delete(key)

    async def close(self):
        """
        Close the Redis connection.
        """
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Redis connection closed")


# Create a singleton instance
redis_client = RedisClient()
