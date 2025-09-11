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

from src.models.events.event import Event
from src.exceptions.invalid_request_exception import InvalidRequestException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class SQSQueueEvent(Event):
    """Represents an AWS Lambda event with parsed parameters."""
    headers: dict
    last_content_type = ""  # Clase variable temporal para Content-Type

    @classmethod
    def from_sqs_record(cls, lambda_event: dict):
        logger.info(f"SQSQueueEvent from_sqs_record lambda_event: {lambda_event}")
        parameters = cls.__get_parameters(lambda_event)
        if not isinstance(parameters, dict):
            raise InvalidRequestException("Invalid event parameters")
        return cls(event_type="sqs", data=parameters, headers=lambda_event.get('headers', {}))
    
    @classmethod
    def __get_parameters(cls, lambda_event: dict) -> dict:
        if 'body' not in lambda_event:
            raise InvalidRequestException("Missing body in event")
        try:
            body = lambda_event['body']
            if isinstance(body, str):
                body = json.loads(body)
            if not isinstance(body, dict):
                raise InvalidRequestException("Body is not a valid JSON object")
            return body
        except json.JSONDecodeError as e:
            raise InvalidRequestException(f"Invalid JSON in body: {e}")