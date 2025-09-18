from typing import Any
from src.event_normalizers.base_event_normalizer import BaseEventHandler
from src.models.events.api_gateway_event import ApiGatewayEvent
from src.utils.headers import get_headers
from src.decorators.log_function_call import log_function_call

class ApiGatewayEventNormalizer(BaseEventHandler):
    def _handler_options_request(self) -> dict:
        return {
            'statusCode': 204,
            'headers': get_headers(),
            'body': ''
        }

    @log_function_call
    def handle(self, event: dict, context: dict, **kwargs: Any) -> dict:
        if event['httpMethod'] == 'OPTIONS':
            return self._handler_options_request()

        lambda_event = ApiGatewayEvent.from_lambda_event(event)
        if self.request_class is None:
            return self.func(lambda_event, context, **kwargs)
        request = self.request_class.from_event(lambda_event)
        return self.func(request, context, **kwargs)