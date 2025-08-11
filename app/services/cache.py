# app/services/cache.py
import json
from typing import Any, Optional, List
import redis.asyncio as aioredis
from app.config.settings import settings

class Cache:
    def __init__(self, url: Optional[str] = None, prefix: Optional[str] = None):
        self._url = url or settings.REDIS_URL
        self._prefix = prefix or settings.REDIS_PREFIX
        self._client: Optional[aioredis.Redis] = None

    async def init(self):
        if self._client is None:
            # decode_responses=True returns str instead of bytes
            self._client = aioredis.from_url(self._url, decode_responses=True)

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        await self.init()
        value = await self._client.get(self._key(key))
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return value

    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        await self.init()
        ex = ex if ex is not None else settings.REDIS_DEFAULT_TTL
        if isinstance(value, (dict, list)):
            to_store = json.dumps(value)
        else:
            to_store = str(value)
        await self._client.set(self._key(key), to_store, ex=ex)

    async def delete(self, key: str):
        await self.init()
        await self._client.delete(self._key(key))

    async def scan_keys(self, pattern: str = "*") -> List[str]:
        """Safely iterate keys using scan (avoid KEYS in production)."""
        await self.init()
        full_pattern = f"{self._prefix}{pattern}"
        keys = []
        async for k in self._client.scan_iter(match=full_pattern):
            # remove prefix for readability
            keys.append(k.replace(self._prefix, "", 1))
        return keys

    async def flush_prefix(self):
        await self.init()
        keys = []
        async for k in self._client.scan_iter(match=f"{self._prefix}*"):
            keys.append(k)
        if keys:
            await self._client.delete(*keys)

    async def info(self) -> dict:
        await self.init()
        return await self._client.info()

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None

    # helper: get or set (atomically read-if-exists else set)
    async def get_or_set(self, key: str, factory, ex: Optional[int] = None):
        val = await self.get(key)
        if val is not None:
            return val
        result = await factory()
        await self.set(key, result, ex=ex)
        return result

# create a module-level instance you can import
cache = Cache()
