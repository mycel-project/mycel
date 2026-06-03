class PendingReviewCache:
    def __init__(self):
        self._pending: str | None = None

    def set(self, node_id: str):
        self._pending = node_id

    def get(self) -> str | None:
        return self._pending

    def clear(self):
        self._pending = None
