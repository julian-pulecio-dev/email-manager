import json
import os
import logging
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
from dataclasses import dataclass

logger = logging.getLogger()
logger.setLevel(logging.INFO)
GOOGLE_ACCOUNT_CREDENTIALS = os.environ['GOOGLE_ACCOUNT_CREDENTIALS']

@dataclass
class VertexIA:
    scopes:str
    project_id:str
    location:str
    model_id:str

    def __get_access_token(self):
        """Obtiene un access token usando la cuenta de servicio."""
        google_account_credentials = json.loads(GOOGLE_ACCOUNT_CREDENTIALS)
        if isinstance(google_account_credentials.get("private_key"), str):
            google_account_credentials["private_key"] = google_account_credentials["private_key"].replace("\\n", "\n")
        logger.info(google_account_credentials)
        credentials = service_account.Credentials.from_service_account_info(
            google_account_credentials,
            scopes=self.scopes
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token
    
    def call_vertex(self, prompt):
        logger.info(f"call vertex with prompt: {prompt[:50]}...")
        """Envía el prompt al endpoint REST de Vertex AI y devuelve la respuesta."""
        token = self.__get_access_token()

        logger.info(f"Token obtenido: {token[:10]}...")
        
        endpoint = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}"
            f"/locations/{self.location}/publishers/google/models/{self.model_id}:generateContent"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        prompt_instruction = """
            From the following text, generate ONLY one JSON object that represents the author's desired action.
            The JSON must have the following format:

            {
            "type": "send_email" | "create_tag", // "send_email" if you want to send an email, "create_tag" if you want to tag emails.
            "date": int, // Date in minutes from the current time (for example, "5" means in 5 minutes).
            "title": string, // Title of the email or tag. If not specified, use a generic title like "Untitled".
            "subject": string, // Subject of the email. If not specified, use the same value as "title".
            "content": string // Message content or tag description.
            }

            Rules:
            - Don't explain anything, just return the JSON.
            - If the time is not specified, assume it is 0 (immediate).
            - If the text is unclear, leave the fields blank except for "type".

            Example:
            Text: "Create a label to organize billing emails"
            Response:
            {
            "type": "create_tag",
            "date": 0,
            "title": "Billing",
            "subject": "Billing",
            "content": "Label for billing emails"
            }

            Input text: " 
        """

        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt_instruction + prompt}]
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