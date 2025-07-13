from src.models.event import Event
from src.utils.headers import get_headers
from src.requests.request import Request

class LambdaDecorator:
    def __init__(self, func=None, *, request_class: Request = None):
        self.func = func
        self.request_class = request_class

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
        lambda_event = Event(event)
        print(f"Lambda event: {lambda_event}")
        request = self.request_class(lambda_event)
        return self.func(request, context)