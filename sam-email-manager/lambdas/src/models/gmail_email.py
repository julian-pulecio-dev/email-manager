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
from src.models.gmail import Gmail


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class GmailEmail(Gmail):
    to: str
    subject: str
    body: str
    attachments: list[File] = None

    def _create_message(self) -> dict:
        message = MIMEMultipart()
        message['to'] = self.to
        message['subject'] = self.subject
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
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment.filename}"'
            )

            message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes())
        return {'raw': raw_message.decode('utf-8')}

    def send(self):
        creds = self._get_access_token()
        service = build("gmail", "v1", credentials=creds)
        message = self._create_message()
        return service.users().messages().send(userId='me', body=message).execute()