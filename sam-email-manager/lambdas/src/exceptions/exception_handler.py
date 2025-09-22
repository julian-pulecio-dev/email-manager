import json
import os
from src.exceptions.custom_exception import CustomException
from src.utils.headers import get_headers
from logging import getLogger, DEBUG

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
        if isinstance(error, CustomException):
            return {
                'statusCode': error.status_code,
                'headers': get_headers(),
                'body': json.dumps({'error': str(error)})
            }
        else:
            if logger.level == DEBUG:
                raise error  # Re-raise the error in debug mode for visibility
            return {
                'statusCode': 500,
                'headers': get_headers(),
                'body': json.dumps({'error': 'An unexpected error occurred'})
            }