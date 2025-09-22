import os
import base64
import logging
from dataclasses import dataclass, field, InitVar

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict, Any
from src.models.dynamo_db import DynamoDBTable
from src.models.gmail_history_event import GmailHistoryEvent
from src.models.gmail import Gmail

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class GmailClient(Gmail):
    dynamo_table: DynamoDBTable = field(
        default_factory=lambda: DynamoDBTable(
            table_name=os.environ['GMAIL_HISTORY_ID_TABLE_NAME']
        )
    )

    def __post_init__(self):
        self.creds = self._get_access_token()
        self.service = build("gmail", "v1", credentials=self.creds, cache_discovery=False)

    def store_user_history_id(self, email: str, history_id: str) -> None:
        self.dynamo_table.put_item({"email": email, "history_id": str(history_id)})

    def retrieve_user_history_id(self, email: str) -> Optional[Dict[str, Any]]:
        return self.dynamo_table.get_item("email", email)

    def get_last_history_id(self) -> Optional[str]:
        try:
            profile = self.service.users().getProfile(userId="me").execute()
            return str(profile.get("historyId")) if profile and profile.get("historyId") else None
        except HttpError as e:
            logger.error(f"Error al obtener el profile de Gmail: {e}")
            return None

    def get_messages_from_history(self, history_id) -> list[GmailHistoryEvent]:
        history_events = self.service.users().history().list(
            userId="me",
            startHistoryId=history_id
        ).execute()

        gmail_messages = []
        for history_event in history_events.get('history', []):
            gmail_history_event = GmailHistoryEvent.from_dict(history_event, self.creds)
            gmail_messages.extend(gmail_history_event.messages_added)
        
        return gmail_messages
