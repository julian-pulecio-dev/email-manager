import boto3
import os
import json
from requests import HTTPError
from urllib3 import PoolManager
from urllib.parse import urlencode
from dataclasses import dataclass
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.exceptions.server_exception import ServerException
from typing import Optional


client = boto3.client('cognito-idp', region_name='us-east-1')

EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN = os.environ.get("EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN")
EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID = os.environ.get("EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID")
CALLBACK_URL = os.environ.get("CALLBACK_URL")

@dataclass
class GoogleSocialAuth:
    def exchange_code_for_tokens(self, code: str) -> dict:
        """Exchanges the authorization code for access tokens."""
        token_url = f"https://{EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN}/oauth2/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID,
            "code": code,
            "redirect_uri": CALLBACK_URL
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = self.__send_code_request(token_url, payload, headers)
        response = self.__validate_response(response)
        response_parsed = self.__parse_oauth_tokens(response)

        return response_parsed

    def __send_code_request(self, token_url, payload, headers) -> dict:
        """Sends the authorization code to the OAuth server to exchange for tokens."""
        http = PoolManager()
        body = urlencode(payload).encode('utf-8')
        try:
            return http.request(
                'POST',
                token_url,
                body=body,
                headers=headers
            )
        except HTTPError as e:
            raise ServerException(f"HTTP Error: {e.status} - {e.reason}")
        except json.JSONDecodeError:
            raise ServerException("Invalid JSON response from OAuth server")
        except Exception as e:
            raise InvalidRequestException("Failed to exchange code for tokens")
    
    def __parse_oauth_tokens(self, response) -> dict:
        """Parses the OAuth tokens from the response data."""
        try:
            response_data = json.loads(response.data.decode('utf-8'))
            return {
                'idToken': response_data.get('id_token'),
                'accessToken': response_data.get('access_token'),
                'refreshToken': response_data.get('refresh_token'),
                'expiresIn': response_data.get('expires_in'),
                'tokenType': response_data.get('token_type')
            }
        except json.JSONDecodeError:
            raise ServerException("Invalid JSON response from OAuth server")
        except KeyError as e:
            raise ServerException(f"Missing key in response data: {e}")
        except Exception as e:
            raise ServerException("Failed to parse OAuth tokens")

    def __validate_response(self, response) -> dict:
        """Validates the response from the OAuth server."""
        if response and response.status == 200:
            return response
        try:
            response_data = json.loads(response.data.decode('utf-8'))
            error_type = response_data.get("error")
            error_desc = response_data.get("error_description", "")
            if error_type == "invalid_request" and "grant_type" in error_desc.lower():
                raise InvalidRequestException(f"Error en grant_type: {error_desc}")
            if error_type == "unsupported_grant_type":
                raise InvalidRequestException(f"grant_type no soportado: {error_desc}")
            if error_type == "invalid_client":
                raise InvalidRequestException(f"Cliente no válido: {error_desc}")
        except json.JSONDecodeError:
            raise ServerException("Invalid JSON response from OAuth server")