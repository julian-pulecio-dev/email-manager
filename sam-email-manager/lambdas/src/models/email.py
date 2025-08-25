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
from src.models.file import File


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class Email:
    to: str
    subject: str
    body: str
    google_oauth_access_token: str
    google_oauth_refresh_token: str
    attachments: list[File] = None

    def __create_message(self) -> dict:
        # Crear mensaje multipart
        message = MIMEMultipart()
        message['to'] = self.to
        message['subject'] = self.subject  # Gmail insertará automáticamente el remitente

        # Cuerpo del mensaje
        msg = MIMEText(self.body, "plain")
        message.attach(msg)

        for attachment in self.attachments or []:    
            fixed_base64 = fix_base64_padding(attachment.content)
            file_bytes = base64.b64decode(fixed_base64)

            mime_type, _ = mimetypes.guess_type(attachment.filename)
            if mime_type is None:
                mime_type = "application/octet-stream"

            main_type, sub_type = mime_type.split("/", 1)

            part = MIMEBase(main_type, sub_type)
            part.set_payload(file_bytes)

            encoders.encode_base64(part)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment.filename}"'
            )

            message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes())
        return {'raw': raw_message.decode('utf-8')}

    def __get_access_token(self):
        return Credentials(
            token=self.google_oauth_access_token,
            refresh_token=self.google_oauth_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"]
        )

    def send(self):
        creds = self.__get_access_token()
        service = build("gmail", "v1", credentials=creds)
        message = self.__create_message()
        return service.users().messages().send(userId='me', body=message).execute()