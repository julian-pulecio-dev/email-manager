from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Tuple
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.models.file import File
import base64
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class GmailMessage:
    id: str
    thread_id: str
    creds : Credentials
    label_ids: List[str] = field(default_factory=list)
    _service: Optional[Any] = field(default=None)
    body_plain: Optional[str] = field(default=None)
    body_html: Optional[str] = field(default=None)
    subject: Optional[str] = field(default=None)
    sender: Optional[str] = field(default=None)
    to: Optional[str] = field(default=None)
    date: Optional[str] = field(default=None)
    attachments: List[File] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict, creds: Credentials) -> "GmailMessage":
        logger.info(f'Parsing GmailMessage from data: {data}')
        message = data.get("message", data)  # más flexible
        if not message or "id" not in message or "threadId" not in message:
            raise ValueError(f"Invalid Gmail message data: {data}")

        return cls(
            id=message["id"],
            thread_id=message["threadId"],
            label_ids=message.get("labelIds", []),
            creds=creds
        )

    def __post_init__(self):
        logger.info(f'Initializing GmailMessage with ID: {self.id}')
        self._get_service()
        self._init_message()


    def _get_service(self):
        if not self._service:
            self._service = build("gmail", "v1", credentials=self.creds, cache_discovery=False)

    def _init_message(
        self, fmt: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """Obtiene el mensaje completo: cuerpo (plain/html) + adjuntos."""
        try:
            message = self._service.users().messages().get(
                userId="me", id=self.id, format=fmt
            ).execute()
            if "payload" not in message:
                logger.warning(f"Message payload not found: {message}")
                raise ValueError("Message payload is missing")

            self.body_plain, self.body_html, self.attachments = self._extract_bodies_and_attachments(
                message.get("payload", {})
            )
            self.headers = self._get_all_headers(message.get("payload", {}))
            logger.debug(f'Processed GmailMessage data: {self.to_dict()}')

        except HttpError as e:
            if e.resp.status == 404:
                logger.error(f"Gmail message not found: {self.id}")
                return None
            logger.error(f"Gmail API error: {e}")
            raise e
        return None

    def _decode_base64url(self, data: str) -> bytes:
        """Decodifica base64-url (con padding)."""
        if not data:
            return b""
        missing_padding = len(data) % 4
        if missing_padding:
            data += "=" * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)

    def _get_all_headers(self, payload: dict) -> dict:
        headers = {h.get("name").lower(): h.get("value") for h in payload.get("headers", [])}
        self.subject = headers.get("subject", "")
        self.sender = headers.get("from", "")
        self.to = headers.get("to", "")
        self.date = headers.get("date", "")
        return headers


    def _extract_bodies_and_attachments(
        self, payload: dict
    ) -> Tuple[Optional[str], Optional[str], List[File]]:

        """
        Extrae cuerpo plain/html y adjuntos de manera recursiva.
        """
        body_plain, body_html = None, None
        attachments: List[File] = []

        def walk_parts(part: dict):
            nonlocal body_plain, body_html, attachments

            mime_type = part.get("mimeType")
            filename = part.get("filename")
            body = part.get("body", {})
            data = body.get("data")
            attachment_id = body.get("attachmentId")

            # Caso: texto plano / html
            if data and not filename:
                decoded = self._decode_base64url(data).decode("utf-8", errors="replace")
                if mime_type == "text/plain" and not body_plain:
                    body_plain = decoded
                elif mime_type == "text/html" and not body_html:
                    body_html = decoded

            # Caso: adjunto
            if filename and (data or attachment_id):
                file_data = None
                if data:
                    file_data = self._decode_base64url(data)
                elif attachment_id:
                    att = self._service.users().messages().attachments().get(
                        userId="me", messageId=self.id, id=attachment_id
                    ).execute()
                    file_data = self._decode_base64url(att["data"])

                attachments.append(
                    File(
                        filename=filename,
                        content=base64.b64encode(file_data).decode("utf-8"),
                        content_type=mime_type
                    )
                )

            # Caso: partes anidadas
            for subpart in part.get("parts", []):
                walk_parts(subpart)

        # recorrer el payload raíz y todas sus partes
        walk_parts(payload)

        return body_plain, body_html, attachments

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a un diccionario."""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "label_ids": self.label_ids,
            "body_plain": self.body_plain,
            "body_html": self.body_html,
            "subject": self.subject,
            "from": self.sender,
            "to": self.to,
            "date": self.date,
        }
    
    def __repr__(self):
        return self.to_dict().__repr__()