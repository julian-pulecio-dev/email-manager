from dataclasses import dataclass
from src.event_requests.event_request import EventRequest

@dataclass
class SQSQueueRequest(EventRequest):
    id: str
    email: str
    name: str | None
    created_at: str
    updated_at: str
    enabled: bool
    status: str