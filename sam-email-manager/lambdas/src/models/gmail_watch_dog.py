import os
import base64
import logging
import mimetypes
from dataclasses import dataclass
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.utils.base64 import fix_base64_padding


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class GmailWatchDog:
    google_oauth_access_token: str
    google_oauth_refresh_token: str
    
    def __get_access_token(self):
        return Credentials(
            token=self.google_oauth_access_token,
            refresh_token=self.google_oauth_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"]
        )

    def check_changes(self, last_history_id: str) -> str | bool:
        creds = self.__get_access_token()
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        if profile.get("historyId") != last_history_id:
            return profile.get("historyId")
        return False