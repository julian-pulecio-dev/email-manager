import json
from src.models.event import Event
from src.utils.headers import get_headers
from src.event_requests.event_request import EventRequest
from dataclasses import dataclass
from dataclasses import dataclass
from typing import Optional, Callable
from dataclasses import field
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.server_exception import ServerException
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel('DEBUG')

@dataclass
class EventParser:
    func: Optional[Callable] = None
    request_class: Optional[EventRequest] = field(default=None, kw_only=True)

    def __call__(self, *args, **kwargs):
        if self.func is not None and len(args) == 1 and callable(args[0]):
            return self

        if len(args) == 2:
            event, context = args
            return self._handle_request(event, context, **kwargs)

        if len(args) == 1 and callable(args[0]):
            self.func = args[0]
            return self

        raise TypeError("Invalid Event Parser arguments")

    def _handle_request(self, event, context, **kwargs):
        """Handles the Lambda event and parses it into a request object."""
        logger.info(f"Received raw event from aws: {json.dumps(event)}")
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 204,
                'headers': get_headers(),
                'body': ''
            }
        lambda_event = Event.from_lambda_event(event)
        logger.info(f"Parsed event: {json.dumps(lambda_event.data)}")
        request = self.request_class.from_event(lambda_event)
        return self.__handle_request_errors(request, context, **kwargs)
        
    def __handle_request_errors(self, request: EventRequest, context, **kwargs):
        """Handles errors that may occur during request processing."""
        try:
            logger.info(f"Processing request: {request}")
            logger.info(f"excecuting function: {self.func.__name__}, with request: {request}, context: {context} and kwargs: {kwargs} ")
            return self.func(request, context, **kwargs)
        except InvalidRequestException as e:
            logger.error(f"Invalid request: {str(e)}")
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': str(e)})
            }
        except ServerException as e:
            logger.error(f"Server error: {str(e)}")
            return {
                'statusCode': 500,
                'headers': get_headers(),
                'body': json.dumps({'error': str(e)})
            }