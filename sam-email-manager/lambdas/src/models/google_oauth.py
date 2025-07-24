import requests
import logging
import jwt
import json
from jwt import PyJWKClient, PyJWKClientError, DecodeError, ExpiredSignatureError, InvalidAudienceError, InvalidSignatureError
from dataclasses import dataclass
from src.exceptions.server_exception import ServerException
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.unauthorized_exception import UnauthorizedException


logger = logging.getLogger()
logger.setLevel(logging.INFO)

JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"

@dataclass
class GoogleOAuth:
    client_id: str
    client_secret: str
    redirect_uri: str

    def exchange_code_for_tokens(self, code: str) ->'GoogleOAuthTokens':
        token_data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
    
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return self.__validate_response(token_response)
    

    def __validate_response(self, token_response) -> dict:
        if token_response.status_code == 200:
            return self.__handle_successful_token_response(token_response)
        return self.__handle_error_token_response(token_response)

    def __handle_successful_token_response(self, token_response) -> 'GoogleOAuthTokens':
        try:
            tokens = token_response.json()
            id_token = tokens.get("id_token")
            if not id_token:
                raise ServerException("id_token not found in the response.")

            decoded = self.__verify_id_token(id_token)
            email = decoded.get("email")
            if not email:
                raise ServerException("email not found in id_token.")

            tokens['email'] = email
            return GoogleOAuthTokens.from_dict(tokens)

        except (json.JSONDecodeError, KeyError) as e:
            raise ServerException(f'Invalid response format: {e}')
        except (DecodeError, InvalidSignatureError, ExpiredSignatureError, InvalidAudienceError) as e:
            raise UnauthorizedException(f'Invalid id_token: {e}')

    def __verify_id_token(self, id_token: str) -> dict:
        try:
            jwks_client = PyJWKClient(JWKS_URL)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            decoded_token = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id
            )
            return decoded_token

        except PyJWKClientError as e:
            logger.error(f"Error retrieving JWKs from Google: {e}")
            raise ServerException("No se pudieron obtener las claves públicas de Google.")
        
        except ExpiredSignatureError:
            logger.warning("El id_token ha expirado.")
            raise UnauthorizedException("El token ha expirado. Por favor, inicia sesión nuevamente.")
        
        except InvalidAudienceError:
            logger.warning("El token fue emitido para un cliente diferente.")
            raise UnauthorizedException("Token inválido: el cliente_id no coincide.")
        
        except InvalidSignatureError:
            logger.warning("Firma inválida en el id_token.")
            raise UnauthorizedException("Token inválido: la firma no es válida.")
        
        except DecodeError as e:
            logger.warning(f"Error al decodificar el id_token: {e}")
            raise UnauthorizedException("Token inválido: no se pudo decodificar.")
        
        except Exception as e:
            logger.error(f"Error inesperado al verificar el id_token: {e}")
            raise ServerException("Ocurrió un error al verificar el token de Google.")


    def __handle_error_token_response(self,token_response) -> dict:
        try:
            error_info = token_response.json()
            
            if token_response.status_code == 400 and "error" in error_info:
                raise InvalidRequestException(f"Error exchanging code for tokens: {error_info.get('error')}")
            
            elif token_response.status_code == 401:
                raise UnauthorizedException(f"Error exchanging code for tokens: {error_info.get('error', 'Unauthorized access.')}")
            
            else:
                raise ServerException(f"Error exchanging code for tokens: {error_info.get('error', 'Unknown error')}")
        
        except json.JSONDecodeError as e:
            raise ServerException(f'Google oauth response has an invalid format {e}')
        
        except KeyError as e:
            raise ServerException(f'error key not found on the google oauth response {e}')

@dataclass
class GoogleOAuthTokens:
    token_type:str
    refresh_token_expires_in:int
    expires_in:str
    id_token:str
    refresh_token:str
    scope:str
    email:str
    access_token:str

    @classmethod
    def from_dict(cls, tokens:dict):
        try:
            return cls(**tokens)
        except TypeError as e:
            raise ServerException(f"Failed to create GoogleOAuthTokens from event: {str(e)}")

    def to_dict(self,):
        return {
            'token_type':self.token_type,
            'refresh_token_expires_in':self.refresh_token_expires_in,
            'id_token':self.id_token,
            'refresh_token':self.refresh_token,
            'scope':self.scope,
            'email':self.email,
            'access_token':self.access_token
        }