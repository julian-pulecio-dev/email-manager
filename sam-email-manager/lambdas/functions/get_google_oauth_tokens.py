import json
import os
import logging
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from src.decorators.lambda_decorator import LambdaDecorator
import google.auth.transport.requests
from src.utils.headers import get_headers
import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_access_token():
    """Obtiene un access token usando la cuenta de servicio."""
    credentials = service_account.Credentials.from_service_account_file(
        'email-manager.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

@LambdaDecorator
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({
            "message": "This is a placeholder response. Implement your logic here."
        })
    }
    # try:
    #     code = event["queryStringParameters"].get("code")
    #     if not code:
    #         return {"statusCode": 400, "body": json.dumps({"error": "No authorization code found"})}

    #     client_id = os.environ.get("GOOGLE_CLIENT_ID")
    #     client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    #     redirect_uri = "https://8ay9rilai8.execute-api.us-east-1.amazonaws.com/dev/get_google_oauth_tokens"

    #     token_data = {
    #         "code": code,
    #         "client_id": client_id,
    #         "client_secret": client_secret,
    #         "redirect_uri": redirect_uri,
    #         "grant_type": "authorization_code"
    #     }

    #     token_response = requests.post(
    #         "https://oauth2.googleapis.com/token",
    #         data=token_data,
    #         headers={"Content-Type": "application/x-www-form-urlencoded"}
    #     )

    #     if token_response.status_code != 200:
    #         logger.error(f"Fallo al intercambiar el código: {token_response.text}")
    #         return {
    #             "statusCode": token_response.status_code,
    #             "body": token_response.text
    #         }

    #     tokens = token_response.json()
    #     id_token = tokens.get("id_token")
    #     if not id_token:
    #         raise Exception("No id_token found in token response")

    #     decoded = jwt.decode(id_token, options={"verify_signature": False})
    #     email = decoded.get("email")

    #     logger.info(f"Tokens recibidos: {json.dumps(tokens)}")
    #     logger.info(f"Email extraído del id_token: {email}")

    #     return {
    #         "statusCode": 200,
    #         "body": json.dumps(tokens),
    #     }

    # except Exception as e:
    #     logger.exception("Error intercambiando el código por tokens")
    #     return {
    #         "statusCode": 500,
    #         "body": json.dumps({"error": str(e)})
    #     }
