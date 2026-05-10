class NullCache:
    def get(self, key: str) -> bytes | None:
        return None

    def set(self, key: str, value: bytes, ttl: int) -> None:
        return None

    def invalidate_prefix(self, prefix: str) -> None:
        return None