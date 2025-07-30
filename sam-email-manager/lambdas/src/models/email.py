import json
import os
import logging
import requests
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.auth.transport.requests
from dataclasses import dataclass

logger = logging.getLogger()
logger.setLevel(logging.INFO)
GOOGLE_ACCOUNT_CREDENTIALS = os.environ['GOOGLE_ACCOUNT_CREDENTIALS']

@dataclass
class Email:
    to: str
    subject: str
    body: str
    google_oauth_access_token: str
    google_oauth_refresh_token: str

    def __create_message(self, to, subject, body):
        """Crea un mensaje de correo electrónico en formato MIME."""
        return {
            'raw': base64.urlsafe_b64encode(
                f'To: {to}\nSubject: {subject}\n\n{body}'.encode('utf-8')
            ).decode('utf-8')
        }
    
    def __get_access_token(self):
        creds = Credentials(
            token=self.google_oauth_access_token,
            refresh_token=self.google_oauth_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ['GOOGLE_CLIENT_ID'],
            client_secret=os.environ['GOOGLE_CLIENT_SECRET']
        )
        return creds

    def send(self):
        creds = self.__get_access_token()
        service = build("gmail", "v1", credentials=creds)
        message = self.__create_message(self.to, self.subject, self.body)
        logger.info(f'Sending email to {self.to} with subject "{self.subject}"')

        result = service.users().messages().send(userId='me', body=message).execute()
        return result