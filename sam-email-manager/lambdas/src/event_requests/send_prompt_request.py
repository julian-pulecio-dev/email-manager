from src.event_requests.event_request import EventRequest
from src.models.file import File
from dataclasses import dataclass, field
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel('DEBUG')

@dataclass
class SendPromptRequest(EventRequest):
    """""
    Request class for handling prompt interpretation.
    """""
    prompt: str
    file: dict

    def __post_init__(self):
        self.file = File(**self.file)