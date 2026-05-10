from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from app.shared.application.ports.cache import CacheService
from app.shared.infrastructure.cache.redis_cache import RedisCache

_singleton: CacheService | None = None


def get_cache() -> CacheService:
    global _singleton
    if _singleton is None:
        _singleton = RedisCache(settings.redis_url)
    return _singleton


CacheDep = Annotated[CacheService, Depends(get_cache)]