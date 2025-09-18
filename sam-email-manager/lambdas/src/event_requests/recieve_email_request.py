from dataclasses import dataclass, InitVar
from base64 import b64decode
import json
from src.event_requests.event_request import EventRequest



@dataclass
class ReceiveEmailRequest(EventRequest):
    """
    Request class for handling email reception.
    """

    def validate(self):
        pass