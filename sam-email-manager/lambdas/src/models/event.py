import base64
import json
from urllib.parse import parse_qs
from dataclasses import dataclass
from src.exceptions.invalid_request_exception import InvalidRequestException

@dataclass
class Event:
    """Represents an AWS Lambda event with parsed parameters."""
    event_type: str
    data: dict
    headers: dict

    @classmethod
    def from_lambda_event(cls, lambda_event: dict):
        """
        Factory method to create an Event instance from a Lambda event dictionary.
        Args:
            lambda_event (dict): The Lambda event dictionary.
        Returns:
            Event: An instance of the Event class.
        """
        return cls(
            event_type=lambda_event.get("event_type"),
            data=json.loads(cls.__get_parameters(lambda_event)),
            headers=lambda_event.get("headers", {})
        )

    @classmethod
    def __get_parameters(cls, lambda_event: dict):
        """Determines the type of parameters to extract based on the HTTP method."""

        http_method = lambda_event.get('httpMethod')
        if http_method == 'GET':
            return cls.__get_querystring_parameters(lambda_event)
        if http_method in ['POST', 'PUT', 'PATCH']:
            return cls.__get_body_parameters(lambda_event)

    @classmethod
    def __get_querystring_parameters(cls, lambda_event: dict) -> dict:
        query_params = lambda_event.get('queryStringParameters', {})
        """Extracts query string parameters from the Lambda event."""

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
        """Extracts body parameters from the Lambda event."""
        
        content_type = lambda_event.get('headers', {}).get('Content-Type', '').lower()
        body = lambda_event.get('body', '')

        if lambda_event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        try:
            if 'application/json' in content_type:
                return json.loads(body)
            elif 'application/x-www-form-urlencoded' in content_type:
                return parse_qs(body)
            else:
                return body
        except Exception as e:
            raise InvalidRequestException(f"Failed to parse body: {str(e)}")

    def __repr__(self):
        return f"Event(event_type={self.event_type}, data={self.data}, headers={self.headers})"




