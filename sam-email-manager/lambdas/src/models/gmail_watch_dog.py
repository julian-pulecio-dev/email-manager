import os
import logging
from dataclasses import dataclass
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.models.gmail import Gmail

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class GmailWatchDog(Gmail):
    def check_changes(self, last_history_id: str) -> str | bool:
        creds = self._get_access_token()
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        if profile.get("historyId") != last_history_id:
            return profile.get("historyId")
        return False