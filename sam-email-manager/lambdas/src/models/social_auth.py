from dataclasses import dataclass
from src.models.google_social_auth import GoogleSocialAuth
from src.exceptions.invalid_request_exception import InvalidRequestException


@dataclass
class SocialAuth:
    def get_access_tokens(self, code: str, provider: str):
        """Method to get access tokens from the social provider."""
        if provider == "Google":
            return self._get_google_access_tokens(code)
        elif provider == "Facebook":
            return self._get_facebook_access_tokens(code)
        raise InvalidRequestException(f'Unsupported provider: {provider}')

    def _get_google_access_tokens(self, code: str):
        social_auth = GoogleSocialAuth()
        return social_auth.exchange_code_for_tokens(code)

    def _get_facebook_access_tokens(self, code: str):
        """Get access tokens from Facebook."""
        raise NotImplementedError("This method should be implemented by subclasses.")