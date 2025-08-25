from typing import List
from src.event_requests.event_request import EventRequest
from src.models.file import File
from dataclasses import dataclass, field, InitVar
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel('DEBUG')

@dataclass
class SendEmailRequest(EventRequest):
    """
    Request class for handling email sending.
    """
    prompt: str
    files: InitVar[List[dict]] = None
    attachments: List[File] = field(default_factory=list)

    def __post_init__(self, files):
        if files:
            self.attachments = [
                File(**file) for file in files
            ]
