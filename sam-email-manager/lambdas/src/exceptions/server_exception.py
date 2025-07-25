class ServerException(Exception):
    """Custom exception class for server errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return f"ServerException: {self.message}"