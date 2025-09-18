class UnauthorizedException(Exception):
    """Exception raised for unauthorized access attempts."""
    
    def __init__(self, message="Unauthorized access."):
        self.status_code = 401
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"UnauthorizedException: {self.message}"