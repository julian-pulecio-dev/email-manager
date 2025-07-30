import json
import os
import logging
import requests
import google.auth.transport.requests
from google.oauth2 import service_account
from src.exceptions.server_exception import ServerException
from src.exceptions.invalid_request_exception import InvalidRequestException
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

        endpoint = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}"
            f"/locations/{self.location}/publishers/google/models/{self.model_id}:generateContent"
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
            response = requests.post(endpoint, headers=headers, json=body).json()
            data = ''
            logger.info(f"Response from Vertex: {response}")
            for candidate in response.get('candidates', []):
                if 'content' in candidate:
                    content = candidate['content']
                    if isinstance(content, dict) and 'parts' in content:
                        for part in content['parts']:
                            if 'text' in part:
                                data += part['text']
            data = data.replace("```json", "").replace("```", "")
            logger.info(f"Data extracted from Vertex response: {data}")
            data = json.loads(data)
            logger.info(f"Parsed data: {data}")           
            if data.get('interpretation_status') == 'success':
                return data
            if data.get('interpretation_status') == 'clarification_needed':
                clarification_message = data.get('clarification_message', 'Please provide more details.')
                logger.info(f'Clarification needed: {clarification_message}')
                raise InvalidRequestException(clarification_message)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al llamar a Vertex: {e}")
            raise ServerException(f"Error al llamar a Vertex: {e}")

        logger.info(f"Response from Vertex: {response.status_code}, {response.text}")

        if response.status_code != 200:
            logger.error(f"Vertex error: {response.status_code}, {response.text}")
            raise ServerException(f"Vertex error: {response.status_code}, {response.text}")

        prediction = response.json()
        logger.info(f"Respuesta Vertex: {json.dumps(prediction)}")
        return prediction