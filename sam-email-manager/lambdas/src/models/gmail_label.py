import os
import logging
from typing import List
from dataclasses import dataclass
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.exceptions.server_exception import ServerException
from src.models.gmail import Gmail


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class GmailLabel(Gmail):
    def __post_init__(self):
        self.creds = self._get_access_token()
        self.service = build("gmail", "v1", credentials=self.creds, cache_discovery=False)

    
    def create_label(self, label_name: str):
        try:
            label_object = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }

            label = self.service.users().labels().create(userId="me", body=label_object).execute()
            return label

        except HttpError as http_err:
            raise ServerException(f"Error HTTP al crear etiqueta: {str(http_err)}")

        except RefreshError as refresh_err:
            raise ServerException(f"Error de autenticación al crear etiqueta: {str(refresh_err)}")

        except Exception as e:
            raise ServerException(f"Error inesperado al crear etiqueta: {str(e)}")


    def move_message_to_label(self, message_id: str, label_ids: List[str]):
        try:
            body = {
                "addLabelIds": label_ids,
                "removeLabelIds": ["INBOX"]
            }

            updated_msg = self.service.users().messages().modify(
                userId="me", 
                id=message_id, 
                body=body
            ).execute()

            return updated_msg

        except HttpError as http_err:
            raise ServerException("Error HTTP al mover mensaje", http_err)