import functools
import json
from collections.abc import Callable
from typing import Any

from app.shared.application.ports.cache import CacheService

_PRIMITIVE = (str, int, float, bool, type(None), list, tuple, dict)


def cached(prefix: str, ttl: int) -> Callable[..., Any]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache: CacheService = kwargs.pop("cache")
            key_payload = {
                k: v for k, v in kwargs.items() if isinstance(v, _PRIMITIVE)
            }
            key = f"{prefix}:{json.dumps(key_payload, default=str, sort_keys=True)}"
            hit = cache.get(key)
            if hit is not None:
                return json.loads(hit)
            result = fn(*args, **kwargs)
            payload = json.dumps(result, default=str).encode("utf-8")
            cache.set(key, payload, ttl=ttl)
            return json.loads(payload)

        return wrapper

    return decorator