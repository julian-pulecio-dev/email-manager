import os
import jwt
import logging
from jwt import PyJWKClient
from dataclasses import dataclass, field
from typing import Optional
from functools import lru_cache
from src.utils.search import get_case_insensitive_value
from src.exceptions.unauthorized_exception import UnauthorizedException
from src.exceptions.forbidden_request_exception import ForbiddenRequestException
from src.exceptions.server_exception import ServerException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EMAIL_MANAGER_AUTH_USER_POOL_ID = os.getenv("EMAIL_MANAGER_AUTH_USER_POOL_ID")
EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID = os.getenv("EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Cacheamos el JWKS client para rendimiento
@lru_cache(maxsize=1)
def get_jwk_client() -> PyJWKClient:
    issuer = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{EMAIL_MANAGER_AUTH_USER_POOL_ID}"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


@dataclass
class Event:
    event_type: str
    data: dict
    headers: dict = field(default_factory=dict)

    def get_user(self) -> Optional[str]:
        """Extrae y valida el usuario desde el JWT en Authorization."""
        auth_header = get_case_insensitive_value(self.headers, "Authorization")
        if not auth_header:
            logger.debug("Authorization header no encontrado")
            return None

        payload = self._decode_and_validate_jwt(auth_header)
        if not payload:
            return None

        return payload.get("email") or payload.get("cognito:username") or payload.get("sub")

    def _decode_and_validate_jwt(self, token: str) -> Optional[dict]:
        """Valida el JWT con JWKS de Cognito."""
        try:
            if token.startswith("Bearer "):
                token = token[7:]

            issuer = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{EMAIL_MANAGER_AUTH_USER_POOL_ID}"

            jwk_client = get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID,
                issuer=issuer,
            )
            return payload

        except (jwt.ExpiredSignatureError,
                jwt.PyJWKClientError) as e:
            raise UnauthorizedException(str(e))
        except (jwt.InvalidAudienceError,
                jwt.MissingRequiredClaimError,
                jwt.InvalidIssuerError,
                jwt.InvalidSignatureError,
                jwt.PyJWKClientError,
                ) as e:
            raise ForbiddenRequestException(str(e))
        except Exception as e:
            raise ServerException(f"Error validando JWT: {e}")