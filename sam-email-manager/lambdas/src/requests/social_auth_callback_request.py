from src.models.event import Event
from src.requests.request import Request
from dataclasses import dataclass

@dataclass
class SocialAuthCallbackRequest(Request):
    code: str
    provider: str