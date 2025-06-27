import json
import os
import logging
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Obtener el código desde el query string
        code = event["queryStringParameters"].get("code")
        if not code:
            return {"statusCode": 400, "body": json.dumps({"error": "No authorization code found"})}

        logger.info(f"Authorization code recibido: {code[:10]}...")

        # Datos necesarios para el intercambio
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        redirect_uri = "https://5whohu7bm0.execute-api.us-east-1.amazonaws.com/dev/hello_world"

        # Preparar el body del POST
        token_data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if token_response.status_code != 200:
            logger.error(f"Fallo al intercambiar el código: {token_response.text}")
            return {
                "statusCode": token_response.status_code,
                "body": token_response.text
            }

        tokens = token_response.json()
        logger.info(f"Tokens recibidos: {json.dumps(tokens)}")

        creds = Credentials(
            token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )

        # Inicializar cliente de Gmail
        service = build("gmail", "v1", credentials=creds)

        # Obtener primeros 5 mensajes del inbox
        results = service.users().messages().list(userId="me", maxResults=5).execute()
        messages = results.get("messages", [])
        logger.info(f"Mensajes obtenidos: {messages}")

        return {
            "statusCode": 200,
            "body": json.dumps({"messages": messages})
        }

    except Exception as e:
        logger.exception("Error intercambiando el código por tokens")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
