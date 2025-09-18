import os
import base64
import logging
import mimetypes
from dataclasses import dataclass
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.utils.base64 import fix_base64_padding
from src.models.file import File


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class Gmail:
    google_oauth_access_token: str
    google_oauth_refresh_token: str
    
    def _get_access_token(self):
        creds = Credentials(
            token=self.google_oauth_access_token,
            refresh_token=self.google_oauth_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"]
        )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds