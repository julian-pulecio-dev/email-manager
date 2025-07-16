class InvalidRequestException(Exception):
    """Exception raised for invalid requests."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return f"InvalidRequestException: {self.message}"