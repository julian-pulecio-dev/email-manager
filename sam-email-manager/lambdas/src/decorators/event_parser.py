import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import Callable, Any, Optional
from src.exceptions.exception_handler import ExceptionHandler
from src.exceptions.server_exception import ServerException
from src.event_requests.event_request import EventRequest
from src.event_normalizers.api_gateway_event_normalizer import ApiGatewayEventNormalizer
from src.event_normalizers.sqs_event_normalizer import SqsEventNormalizer

logger = getLogger(__name__)
logger.setLevel(os.getenv("LOGGER_LEVEL", "NOTSET"))

@dataclass
class EventParser:
    func: Optional[Callable] = field(init=False, default=None)
    request_class: Optional[type[EventRequest]] = field(default=None, kw_only=True)

    def __call__(self, func: Callable) -> Callable:
        self.func = func

        def wrapper(event: dict, context: dict, **kwargs: Any) -> Any:
            try:
                if "httpMethod" in event:
                    return ApiGatewayEventNormalizer(func, self.request_class).handle(event, context, **kwargs)
                if "Records" in event:
                    return SqsEventNormalizer(func, self.request_class).handle(event, context, **kwargs)
                raise ServerException("Unsupported event type")
            except Exception as e:
                return ExceptionHandler.handle_exception(e)

        return wrapper
