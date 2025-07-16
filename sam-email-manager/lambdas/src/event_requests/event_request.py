from src.models.event import Event
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.server_exception import ServerException

class EventRequest:
    @classmethod
    def from_event(cls, event: Event):
        """
        Factory method to create a Request instance from an Event.
        Args:
            event (Event): The Event instance.
        Returns:
            Request: An instance of the Request class.
        """
        try:
            return cls(**event.data)
        except TypeError as e:
            raise InvalidRequestException(f"Invalid event data for {cls.__name__}: {e}")
        except Exception as e:
            raise ServerException(f"Failed to create request from event: {str(e)}")