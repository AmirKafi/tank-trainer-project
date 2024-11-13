from abc import ABC, abstractmethod

import redis.asyncio as redis

from config import get_redis_host_and_port

# Initialize Redis connection
redis = redis.Redis(**get_redis_host_and_port(), db=0)

class AbstractMemoryCacheRepository(ABC):

    @abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abstractmethod
    def set(self, key, value,expires):
        raise NotImplementedError

    @abstractmethod
    def delete(self, key):
        raise NotImplementedError


class MemoryCacheRepository(AbstractMemoryCacheRepository):

    async def get(self, key):
        return await redis.get(key)

    async def set(self, key, value, expires:int):
        await redis.set(key, value, expires)

    async def delete(self, key):
        await redis.delete(key)