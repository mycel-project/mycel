from collections import defaultdict
from typing import Callable, Awaitable, Any

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable[[Any], Awaitable]]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[[Any], Awaitable]) -> None:
        self._handlers[event_type].append(handler)

    async def emit(self, event_type: str, data: Any = None) -> None:
        for handler in self._handlers.get(event_type, []):
            await handler(data)
