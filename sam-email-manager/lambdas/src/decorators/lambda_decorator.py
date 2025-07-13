from src.models.event import Event
from src.utils.headers import get_headers

class LambdaDecorator:
    """
    Decorator to handle AWS Lambda events.
    It processes the event and returns a response.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, event, context):
        print(event)
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 204,
                'headers': get_headers(),
                'body': ''
            }
        lambda_event = Event(event)
        return self.func(lambda_event, context)