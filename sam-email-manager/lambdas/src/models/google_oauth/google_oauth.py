import requests
import logging
import jwt
import json
from dataclasses import dataclass
from src.exceptions.server_exception import ServerException
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.unauthorized_exception import UnauthorizedException


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class GoogleOAuth:
    client_id: str
    client_secret: str
    redirect_uri: str

    def exchange_code_for_tokens(self, code: str) ->dict:
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

    def __handle_successful_token_response(self,token_response) -> dict:
        try:
            tokens = token_response.json()
            id_token = tokens.get("id_token")
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            email = decoded.get("email")
            tokens['email'] = email
            return tokens
        except json.JSONDecodeError as e:
            raise ServerException(f'Google oauth response has an invalid format {e}')
        except KeyError as e:
            raise ServerException(f'id_token not found on the google oauth response {e}')

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
    