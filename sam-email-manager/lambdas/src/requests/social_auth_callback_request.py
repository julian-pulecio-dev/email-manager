from src.models.event import Event
from src.requests.request import Request

class SocialAuthCallbackRequest(Request):
    def __init__(self, event: Event):
        print(event.data)
        self.code = event.data.get('code')
        if not self.code:
            raise ValueError("Missing 'code' parameter in the request data.")
        