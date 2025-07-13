import base64
import json
from urllib.parse import parse_qs


class Event:
    def __init__(self, lambda_event: dict):
        self.event_type = lambda_event.get("event_type")
        self.data = json.loads(self.__get_parameters(lambda_event))
        self.headers = lambda_event.get("headers", {})

    def __get_parameters(self, lambda_event: dict):
        http_method = lambda_event.get('httpMethod')
        if http_method == 'GET':
            return self.__get_querystring_parameters(lambda_event)
        if http_method in ['POST', 'PUT', 'PATCH']:
            return self.__get_body_parameters(lambda_event)

    def __get_querystring_parameters(self, lambda_event: dict) -> dict:
        query_params = lambda_event.get('queryStringParameters', {})
        multi_value_params = lambda_event.get('multiValueQueryStringParameters', {})
            
        parsed_params = {**query_params} if query_params else {}
        for key, values in multi_value_params.items():
            if len(values) == 1:
                parsed_params[key] = values[0]
            else:
                parsed_params[key] = values
            
            return parsed_params
    
    def __get_body_parameters(self, lambda_event: dict) -> dict:
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
            raise ValueError(f"Failed to parse body: {str(e)}")

    def __repr__(self):
        return f"Event(event_type={self.event_type}, data={self.data}, headers={self.headers})"




