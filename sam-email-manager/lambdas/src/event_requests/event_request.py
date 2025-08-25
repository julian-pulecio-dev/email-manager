from src.models.event import Event
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.server_exception import ServerException
from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel('DEBUG')


@dataclass 
class EventRequest:
    @classmethod
    def from_event(cls, event: "Event"):
        """
        Factory method to create a Request instance from an Event.
        Args:
            event (Event): The Event instance.
        Returns:
            Request: An instance of the Request class.
        """
        try:
            logger.info(f"Creating {cls.__name__} from event data: {event.data}")
            instance = cls(**event.data)
            instance.__set_headers(event.headers)
            instance.__set_user(event.get_user())
            return instance
        except TypeError as e:
            raise InvalidRequestException(f"Invalid event data for {cls.__name__}: {e}")
        except Exception as e:
            raise ServerException(f"Failed to create request from event: {str(e)}")
    
    def __set_headers(self, headers:dict):
        self.headers = headers
    
    def __set_user(self, user):
        self.user = user