import os
from logging import getLogger
from dataclasses import dataclass
from abc import abstractmethod
from src.models.events.api_gateway_event import Event
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.server_exception import ServerException

logger = getLogger(__name__)
logger.setLevel(os.environ.get("LOGGER_LEVEL", "INFO"))

@dataclass 
class EventRequest:
    @classmethod
    def from_event(cls, event: "Event"):
        try:
            instance = cls(**event.data)
            instance._set_headers(event.headers)
            instance._set_user(event.get_user())
            instance._set_raw_event(event)
            return instance
        except TypeError as e:
            raise InvalidRequestException(f"Invalid event data for {cls.__name__}: {e}")
    
    def _set_headers(self, headers:dict):
        self.headers = headers
    
    def _set_user(self, user):
        self.user = user
    
    def _set_raw_event(self, raw_event:dict):
        self.raw_event = raw_event
    
    @abstractmethod
    def validate(self):
        pass