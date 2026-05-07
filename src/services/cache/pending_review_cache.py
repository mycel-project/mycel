class PendingReviewCache:
    def __init__(self):
        self._pending: int | None = None

    def set(self, node_id: int):
        self._pending = node_id

    def get(self) -> int | None:
        return self._pending

    def clear(self):
        self._pending = None
