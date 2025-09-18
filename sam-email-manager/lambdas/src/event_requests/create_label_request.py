from dataclasses import dataclass, InitVar
from src.event_requests.event_request import EventRequest


@dataclass
class CreateLabelRequest(EventRequest):
    """
    Request class for handling label creation.
    """
    instruction: str
    title: str

    def validate(self):
        pass