import logging
from dataclasses import dataclass
from google.oauth2.credentials import Credentials
from src.models.gmail_message import GmailMessage

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class GmailHistoryEvent:
    messages_added: list[GmailMessage]
    creds: Credentials

    @classmethod
    def from_dict(cls, data: dict, creds: Credentials) -> "GmailHistoryEvent":
        return cls(
            messages_added=[
                GmailMessage.from_dict(msg, creds) for msg in data.get("messagesAdded", [])
            ],
            creds=creds
        )
