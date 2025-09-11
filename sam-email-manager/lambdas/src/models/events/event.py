import base64
import json
import logging
from urllib.parse import parse_qs
from dataclasses import dataclass
from io import BytesIO
from src.utils.search import get_case_insensitive_value

from werkzeug.wrappers import Request
from werkzeug.test import EnvironBuilder
from werkzeug.formparser import parse_form_data

from src.exceptions.invalid_request_exception import InvalidRequestException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class Event:
    """Represents an AWS Lambda event with parsed parameters."""
    event_type: str
    data: dict
    headers: dict = None

    def get_user(self):
        if 'Authorization' not in self.headers:
            return None
        auth_header = self.headers.get('Authorization')
        payload = self.__decode_auth_header_jwt(auth_header)
        if not payload or 'email' not in payload:
            return None
        return payload.get('email')

    def __decode_auth_header_jwt(self, token: str) -> dict | None:
        if not token:
            return None
        try:
            if token.startswith('Bearer '):
                token = token[7:]

            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError('El token no tiene el formato JWT correcto')

            def decode_base64(data):
                padding = len(data) % 4
                if padding:
                    data += '=' * (4 - padding)
                return base64.urlsafe_b64decode(data).decode('utf-8')

            payload = json.loads(decode_base64(parts[1]))
            return payload
        except Exception as error:
            logger.error(f'Error al decodificar el token JWT: {error}')
            return None