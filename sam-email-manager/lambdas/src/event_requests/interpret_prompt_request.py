from src.event_requests.event_request import EventRequest
from dataclasses import dataclass

@dataclass
class InterpretPromptRequest(EventRequest):
    """""
    Request class for handling prompt interpretation.
    """""
    prompt: str