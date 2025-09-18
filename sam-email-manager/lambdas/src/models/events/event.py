import os
import jwt
import logging
from jwt import PyJWKClient
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from functools import lru_cache
from src.utils.search import get_case_insensitive_value
from src.exceptions.unauthorized_exception import UnauthorizedException
from src.exceptions.forbidden_request_exception import ForbiddenRequestException
from src.exceptions.server_exception import ServerException
import time

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


class JwtValidator:
    """Encapsula la validación de JWTs firmados por Cognito con logging de expiración y leeway."""

    def __init__(self, region: str, user_pool_id: str, client_id: str, leeway: int = 10):
        """
        :param leeway: segundos de margen para desfase de reloj
        """
        self.region = region
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.leeway = leeway
        self.issuer = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"

    def validate(self, token: str) -> Dict[str, Any]:
        """Valida el token JWT y devuelve el payload decodificado."""
        try:
            if token.startswith("Bearer "):
                token = token[7:]

            jwk_client = get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer,
                leeway=self.leeway  # margen para desfase de reloj
            )
            return payload

        except jwt.ExpiredSignatureError as e:
            # Mostrar claramente los tiempos y el desfase
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                iat = payload.get("iat")
                exp = payload.get("exp")
                now = int(time.time())
                logger.warning(
                    f"JWT expirado: iat={iat}, exp={exp}, now={now}, desfase={now - exp}s"
                )
            except Exception:
                logger.warning("JWT expirado, no se pudo decodificar el payload sin verificar la firma")

            raise UnauthorizedException(f"JWT expirado: {e}")

        except (jwt.InvalidAudienceError,
                jwt.MissingRequiredClaimError,
                jwt.InvalidIssuerError,
                jwt.InvalidSignatureError) as e:
            logger.warning(f"JWT inválido: {e}")
            raise ForbiddenRequestException(str(e))

        except jwt.PyJWKClientError as e:
            logger.error(f"Error obteniendo JWKS: {e}")
            raise ServerException(str(e))

        except Exception as e:
            logger.exception("Error inesperado validando JWT")
            raise ServerException(f"Error validando JWT: {e}")


@dataclass
class Event:
    event_type: str
    data: dict
    headers: dict = field(default_factory=dict)
    jwt_validator: JwtValidator = field(
        default_factory=lambda: JwtValidator(
            AWS_REGION,
            EMAIL_MANAGER_AUTH_USER_POOL_ID,
            EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID,
        )
    )

    def get_user(self) -> Optional[str]:
        """Extrae y valida el usuario desde el JWT en Authorization."""
        auth_header = get_case_insensitive_value(self.headers, "Authorization")
        if not auth_header:
            logger.debug("Authorization header no encontrado")
            return None

        payload = self.jwt_validator.validate(auth_header)
        return payload.get("email") or payload.get("cognito:username") or payload.get("sub")
