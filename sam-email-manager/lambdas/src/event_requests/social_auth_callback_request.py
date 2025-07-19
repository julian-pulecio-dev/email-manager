from src.event_requests.event_request import EventRequest
from dataclasses import dataclass

@dataclass
class SocialAuthCallbackRequest(EventRequest):
    code: str
    provider: str