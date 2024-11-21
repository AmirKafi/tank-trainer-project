from adapters.repositories.MemoryCacheRepository import MemoryCacheRepository


async def get_redis_cache(key:str):
    repo = MemoryCacheRepository()
    return await repo.get(key)

async def set_redis_cache(
        key:str,
        value:str,
        expires:int
)->None:
    repo = MemoryCacheRepository()
    await repo.set(key, value, expires)

async def delete_redis_cache(key:str):
    repo = MemoryCacheRepository()
    await repo.delete(key)