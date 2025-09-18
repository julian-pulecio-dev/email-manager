from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from src.event_requests.event_request import EventRequest

class BaseEventHandler(ABC):
    def __init__(self, func: Callable, request_class: Optional[type[EventRequest]] = None):
        self.func = func
        self.request_class = request_class

    @abstractmethod
    def handle(self, event: dict, context: dict, **kwargs: Any) -> Any:
        """Handle the event and return a response"""
        pass