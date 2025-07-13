import json
import os
import logging
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.auth.transport.requests

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

def call_vertex(prompt):
    logger.info(f"call vertex with prompt: {prompt[:50]}...")
    """Envía el prompt al endpoint REST de Vertex AI y devuelve la respuesta."""
    token = get_access_token()

    logger.info(f"Token obtenido: {token[:10]}...")
    
    # Personaliza estos valores:
    project_id = 'email-manager-445502'  # recomendado pasarlo por variables de entorno
    location = "us-central1"  # o tu región de Vertex AI
    model_id = "gemini-1.5-flash"  # ejemplo con modelo generativo de texto

    endpoint = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}"
        f"/locations/{location}/publishers/google/models/{model_id}:generateContent"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }
    logger.info(f"Enviando solicitud a Vertex: {json.dumps(body)}")

    try:
        response = requests.post(endpoint, headers=headers, json=body)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al llamar a Vertex: {e}")
        raise Exception(f"Error al llamar a Vertex: {e}")

    logger.info(f"Response from Vertex: {response.status_code}, {response.text}")

    if response.status_code != 200:
        logger.error(f"Vertex error: {response.status_code}, {response.text}")
        raise Exception(f"Vertex error: {response.status_code}, {response.text}")

    prediction = response.json()
    logger.info(f"Respuesta Vertex: {json.dumps(prediction)}")
    return prediction

def lambda_handler(event, context):
    try:
        prompt = "Dime un chiste corto."
        gemini_response = call_vertex(prompt)
        return {
            "statusCode": 200,
            "body": json.dumps(gemini_response),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
