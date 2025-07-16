from src.models.event import Event
from src.utils.headers import get_headers
from src.requests.request import Request
from dataclasses import dataclass
from dataclasses import dataclass
from typing import Optional, Callable
from dataclasses import field

@dataclass
class LambdaDecorator:
    func: Optional[Callable] = None
    request_class: Optional[Request] = field(default=None, kw_only=True)

    def __call__(self, *args, **kwargs):
        if self.func is not None and len(args) == 1 and callable(args[0]):
            return self

        if len(args) == 2:
            event, context = args
            return self._handle_request(event, context)

        if len(args) == 1 and callable(args[0]):
            self.func = args[0]
            return self

        raise TypeError("Invalid arguments")

    def _handle_request(self, event, context):
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 204,
                'headers': get_headers(),
                'body': ''
            }
        lambda_event = Event.from_lambda_event(event)
        print(f"Lambda event: {lambda_event}")
        request = self.request_class.from_event(lambda_event)
        return self.func(request, context)