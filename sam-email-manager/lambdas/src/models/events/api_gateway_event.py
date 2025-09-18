import base64
import json
import logging
import os
from io import BytesIO
from urllib.parse import parse_qs
from dataclasses import dataclass
from werkzeug.wrappers import Request
from werkzeug.test import EnvironBuilder
from werkzeug.formparser import parse_form_data
from src.models.events.event import Event
from src.utils.search import get_case_insensitive_value
from src.exceptions.invalid_request_exception import InvalidRequestException

logger = logging.getLogger()
logger.setLevel(os.getenv("LOGGER_LEVEL", "NOTSET"))

@dataclass
class ApiGatewayEvent(Event):
    """Represents an AWS Lambda event with parsed parameters."""
    @classmethod
    def from_lambda_event(cls, lambda_event: dict):
        parameters = cls._get_parameters(lambda_event)
        if not isinstance(parameters, dict):
            parameters = json.loads(parameters)
        return cls(
            event_type=lambda_event.get("event_type", "unknown"),
            data=parameters,
            headers=lambda_event.get("headers", {})
        )

    @classmethod
    def _get_parameters(cls, lambda_event: dict):
        http_method = lambda_event.get('httpMethod')
        if http_method == 'GET':
            return cls._get_querystring_parameters(lambda_event)
        if http_method in ['POST', 'PUT', 'PATCH']:
            return cls._get_body_parameters(lambda_event)

    @classmethod
    def _get_querystring_parameters(cls, lambda_event: dict) -> dict:
        query_params = lambda_event.get('queryStringParameters', {})
        multi_value_params = lambda_event.get('multiValueQueryStringParameters', {})

        parsed_params = {**query_params} if query_params else {}
        for key, values in multi_value_params.items():
            parsed_params[key] = values if len(values) > 1 else values[0]

        return parsed_params

    @classmethod
    def _get_body_parameters(cls, lambda_event: dict) -> dict:
        content_type = get_case_insensitive_value(lambda_event.get('headers', {}), 'content-type')
        body = lambda_event.get('body', '') or b""
        
        if lambda_event.get('isBase64Encoded', False):
            body = base64.b64decode(body)
        
        elif isinstance(body, str):
            body = body.encode("utf-8")
        
        elif not isinstance(body, bytes):
            body = bytes(body)

        body_len = len(body)
        
        if 'application/json' in content_type:
            if body:
                return json.loads(body.decode("utf-8"))
            return {}
        
        elif 'multipart/form-data' in content_type:
            return cls._get_multipart_form_data(body, body_len, content_type)
        
        elif 'application/x-www-form-urlencoded' in content_type:
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(body).items()}
        
        else:
            return body

    @classmethod
    def _get_multipart_form_data(cls, body: bytes, body_len: int, content_type: str) -> dict:
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
        _, form, files = parse_form_data(env)

        result = {}

        for key in form:
            result[key] = form.getlist(key) if len(form.getlist(key)) > 1 else form.get(key)

        for key in files:
            file_list = files.getlist(key)
            result[key] = []
            for file in file_list:
                content_file = file.read()
                content_b64 = base64.b64encode(content_file).decode("utf-8")
                result[key].append({
                    'filename': file.filename,
                    'content': content_b64,
                    'content_type': file.content_type
                })

        return result

    def __repr__(self):
        return f"Event(event_type={self.event_type}, data={self.data}, headers={self.headers})"
