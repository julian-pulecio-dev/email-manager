class ForbiddenRequestException(Exception):
    """Exception raised for invalid requests."""
    def __init__(self, message: str):
        self.status_code = 403
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return f"ForbiddenRequestException: {self.message}"