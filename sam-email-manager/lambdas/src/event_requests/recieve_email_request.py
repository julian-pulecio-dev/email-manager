from dataclasses import dataclass, InitVar
from base64 import b64decode
import json
from src.event_requests.event_request import EventRequest



@dataclass
class ReceiveEmailRequest(EventRequest):
    """
    Request class for handling email reception.
    """
    message: InitVar[dict]
    subscription: str

    def __post_init__(self, message: dict):
        message_data = json.loads(b64decode(message['data']).decode('utf-8'))
        self.email_address = message_data.get("emailAddress")
        self.history_id = message_data.get("historyId")
    
    def __repr__(self):
        return f"ReceiveEmailRequest(subscription={self.subscription}, email_address={self.email_address}, history_id={self.history_id})"