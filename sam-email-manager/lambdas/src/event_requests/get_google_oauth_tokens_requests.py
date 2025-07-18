from src.event_requests.event_request import EventRequest
from dataclasses import dataclass

@dataclass
class GetGoogleOAuthTokensRequest(EventRequest):
    """
    Request class for handling social authentication token retrieval.
    """
    code: str