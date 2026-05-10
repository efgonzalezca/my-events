class FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    def get(self, key: str) -> bytes | None:
        return self.store.get(key)

    def set(self, key: str, value: bytes, ttl: int) -> None:
        self.store[key] = value

    def invalidate_prefix(self, prefix: str) -> None:
        for key in [k for k in self.store if k.startswith(prefix)]:
            del self.store[key]