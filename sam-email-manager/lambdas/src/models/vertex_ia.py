import json
import os
import logging
import requests
import base64
from typing import List
import google.auth.transport.requests
from google.oauth2 import service_account
from src.exceptions.server_exception import ServerException
from src.exceptions.invalid_request_exception import InvalidRequestException
from src.models.file import File
from src.decorators.log_function_call import log_function_call
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

    def _get_access_token(self):
        """Obtiene un access token usando la cuenta de servicio."""
        google_account_credentials = json.loads(GOOGLE_ACCOUNT_CREDENTIALS)
        if isinstance(google_account_credentials.get("private_key"), str):
            google_account_credentials["private_key"] = google_account_credentials["private_key"].replace("\\n", "\n")
        credentials = service_account.Credentials.from_service_account_info(
            google_account_credentials,
            scopes=self.scopes
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def call_vertex(self, prompt: str, files: List[File] = []):
        """Envía el prompt al endpoint REST de Vertex AI y devuelve la respuesta."""
        token = self._get_access_token()
        endpoint = self._get_vertex_endpoint()
        headers = self._get_headers(token)
        body = self._get_body(prompt, files)

        try:
            response = requests.post(endpoint, headers=headers, json=body)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise ServerException(f"Error al llamar a Vertex: {e}")
    
    def _get_vertex_endpoint(self):
        """Construye el endpoint de Vertex AI."""
        return (
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}"
            f"/locations/{self.location}/publishers/google/models/{self.model_id}:generateContent"
        )
    
    def _get_headers(self, token):
        """Construye los headers necesarios para la solicitud a Vertex AI."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get_body(self, prompt, files: List[File]=[]):
        parts = [{"text": prompt}]

        for file in files:
            parts.append({
                "inlineData": {
                    "mimeType": file.content_type,
                    "data": file.content
                }
            })

        return {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ]
        }
    
    def _handle_response(self, response):
        """Handles the response from Vertex AI and extracts the text content."""
        if response.status_code == 200:
            return self._handle_success_response(response)
        return self._handle_error_response(response)
        
    def _handle_success_response(self, response):
        """Handles successful responses from Vertex AI."""
        response_text = response.text.replace("```json", '').replace("```", '')
        response = json.loads(response_text)
        if 'candidates' not in response or len(response['candidates']) <= 0:
            raise ServerException("No candidates found in Vertex AI response.")
        
        text_response = response['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not text_response:
            raise ServerException("No text found in Vertex AI response.")
    
        json_response = self._parse_json_from_text(text_response)

        if json_response.get('interpretation_status') == 'clarification_needed':
            raise InvalidRequestException(f"clarification needed. reason: {json_response.get('clarification_message')}")

        return json_response
    
    def _handle_error_response(self, response):
        """Handles error responses from Vertex AI."""
        if response.status_code == 400:
            raise InvalidRequestException(f'Bad request to Vertex AI: {response.text}')
        elif response.status_code == 401:
            raise ServerException(f"Unauthorized access to Vertex AI: {response.text}")
        elif response.status_code == 403:
            raise ServerException(f"Forbidden access to Vertex AI: {response.text}")
        elif response.status_code == 404:
            raise ServerException(f"Vertex AI endpoint not found: {response.text}")
        else:
            raise ServerException(f"Unexpected error from Vertex AI: {response.status_code}")
    
    @log_function_call
    def _parse_json_from_text(self, text):
        """Parses a JSON object from a text string."""
        try:
            json_response = json.loads(text)
            if 'interpretation_status' not in json_response:
                raise ServerException("Invalid JSON response from Vertex AI: 'interpretation_status' key not found.")
            return json_response
        except json.JSONDecodeError as e:
            raise ServerException(f"Failed to parse JSON from text: {str(e)}")