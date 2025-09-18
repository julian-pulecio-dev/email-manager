from src.exceptions.custom_exception import CustomException

class InvalidRequestException(CustomException):
    """Exception raised for invalid requests."""
    def __init__(self, message: str):
        self.status_code = 400
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return f"InvalidRequestException: {self.message}"