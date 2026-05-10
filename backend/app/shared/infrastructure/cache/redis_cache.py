import redis


class RedisCache:
    def __init__(self, url: str) -> None:
        self._r = redis.Redis.from_url(url)

    def get(self, key: str) -> bytes | None:
        return self._r.get(key)

    def set(self, key: str, value: bytes, ttl: int) -> None:
        self._r.set(key, value, ex=ttl)

    def invalidate_prefix(self, prefix: str) -> None:
        for key in self._r.scan_iter(match=f"{prefix}*"):
            self._r.unlink(key)