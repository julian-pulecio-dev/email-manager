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
from src.exceptions.server_exception import ServerException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class Event:
    """Represents an AWS Lambda event with parsed parameters."""
    event_type: str
    data: dict
    headers: dict

    last_content_type = ""  # Clase variable temporal para Content-Type

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

    @classmethod
    def from_lambda_event(cls, lambda_event: dict):
        parameters = cls.__get_parameters(lambda_event)
        if not isinstance(parameters, dict):
            parameters = json.loads(parameters)
        return cls(
            event_type=lambda_event.get("event_type", "unknown"),
            data=parameters,
            headers=lambda_event.get("headers", {})
        )

    @classmethod
    def __get_parameters(cls, lambda_event: dict):
        http_method = lambda_event.get('httpMethod')
        if http_method == 'GET':
            return cls.__get_querystring_parameters(lambda_event)
        if http_method in ['POST', 'PUT', 'PATCH']:
            return cls.__get_body_parameters(lambda_event)

    @classmethod
    def __get_querystring_parameters(cls, lambda_event: dict) -> dict:
        query_params = lambda_event.get('queryStringParameters', {})
        multi_value_params = lambda_event.get('multiValueQueryStringParameters', {})

        parsed_params = {**query_params} if query_params else {}
        for key, values in multi_value_params.items():
            if len(values) == 1:
                parsed_params[key] = values[0]
            else:
                parsed_params[key] = values

        return parsed_params

    @classmethod
    def __get_body_parameters(cls, lambda_event: dict) -> dict:
        content_type = get_case_insensitive_value(lambda_event.get('headers', {}), 'content-type')
        cls.last_content_type = content_type  # Guardar content-type

        body = lambda_event.get('body', '')
        body_len = len(body)

        if lambda_event.get('isBase64Encoded', False):
            
            body = base64.b64decode(body)

        
        if 'application/json' in content_type:
                return json.loads(body)
        elif 'multipart/form-data' in content_type:
            return cls.__get_multipart_form_data(body, body_len)
        elif 'application/x-www-form-urlencoded' in content_type:
                return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(body).items()}
        else:
            return body

    @classmethod
    def __get_multipart_form_data(cls, body: bytes, body_len: int) -> dict:
        content_type = cls.last_content_type
        if not content_type.startswith("multipart/form-data"):
            raise InvalidRequestException("Invalid content-type for multipart parsing")
        bytes_body = BytesIO(body)
        builder = EnvironBuilder(
            method="POST",
            input_stream=bytes_body,
            content_type=content_type,
            content_length=body_len
        )
        env = builder.get_environ()
        request = Request(env)

        _, form, files = parse_form_data(env)

        logger.info(f"Parsed form data: {form}")

        result = {}

        for key in form:
            result[key] = form.get(key)

        for key in files:
            file = files[key]
            content_file = file.read()
            content_b64 = base64.b64encode(content_file)
            result[key] = {
                'filename': file.filename,
                'content': content_b64,
                'content_type': file.content_type
            }

        return result

    def __repr__(self):
        return f"Event(event_type={self.event_type}, data={self.data}, headers={self.headers})"
