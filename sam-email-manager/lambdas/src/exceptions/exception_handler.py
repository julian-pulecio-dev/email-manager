import json
import os
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.server_exception import ServerException
from src.utils.headers import get_headers
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel(os.getenv("LOGGER_LEVEL", "NOTSET"))

class ExceptionHandler:
    @staticmethod
    def handle_exception(error: Exception) -> dict:
        """
        Handles exceptions and returns a standardized error response.
        Args:
            error (Exception): The exception to handle.
        Returns:
            dict: The standardized error response.
        """
        logger.error(f"Exception occurred: {str(error)}") 
        if isinstance(error, InvalidRequestException):
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': str(error)})
            }
        elif isinstance(error, ServerException):
            return {
                'statusCode': 500,
                'headers': get_headers(),
                'body': json.dumps({'error': str(error)})
            }
        elif isinstance(error, json.JSONDecodeError):
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Invalid JSON format'})
            }
        else:
            return {
                'statusCode': 500,
                'headers': get_headers(),
                'body': json.dumps({'error': 'An unexpected error occurred'})
            }