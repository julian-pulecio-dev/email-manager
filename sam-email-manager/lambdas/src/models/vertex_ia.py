import json
import os
import logging
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.auth.transport.requests
from dataclasses import dataclass

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class VertexIA:
    scopes:str
    project_id:str
    location:str
    model_id:str

    def __get_access_token(self):
        """Obtiene un access token usando la cuenta de servicio."""
        credentials = service_account.Credentials.from_service_account_info(
            {
            "type": "service_account",
            "project_id": "email-manager-445502",
            "private_key_id": "f42fd95392244768c19b05dc5a6aa2aafcae26b9",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDQiHx+Ebt88SaJ\nc1cYHFSXFDdlpgNd1vd/x9rN0gQOv5OiaPhjS/GMOIU2/i7FhQuIkuVLCPG7Z5Hc\nNuuYMOMJKkA7DyJUj4u+wG0VBTYjGtn1YZAPt+W5aZI/t/U00Pah0+XgiXCAxP7v\nGAbSh6BvcrM1XxdGNro9PGM2gZOK1vnvdsJbdK5DB0Dc2ND+KYnB77P5nH+DGDTh\n64v3iaRQ5Z0WD9GmosJQrcWMFTagKxGLQZfEVDnQbcVOj9TUpeIGIKv3EW0BofI4\nH9p04iuU8YsN+G6BkBOEgwijYAiKtD+PiqB0LWt1aby8SZCfVXANkUTpFNtzkWqw\nQD6zF0SRAgMBAAECggEAMGoXuS9Fv66/Ozc3l8XwD7lmWSevbWh8wsJ0NsfVIFVz\nIchMLsWReXQf3ZIq6rnGYTl1mbOkZ9WWZDGuBgIHm/eevPd5CXfgQnOrf69bj8/q\nnZE+oJ+Z6q+rgDal69K+B/lJzBUstQDHjVwfLV7GrUlMeQ4wOaF4IMJ16FAyII/4\nFJi4smvJ6S6NK1C64T96nqEF1OWq1bSynrrdMGQmN1sIrEr5tVH0PzMhQ4D/n0fT\n/elP4G3Kl/Wtsgcb+uFHKboEjJyYIukv7Xd84Lom6MXd+WFAaTBfORuJPhDo2xJp\nLHwlzHeIn7lldx8ceHRF5MJEzUf0jOaExZYNpUdz5wKBgQD5KJro+QojqEfkcIW9\nwqzgKIIMNJIAth/AMhNrao9s2l62dt5QidPfi+3BLK2D/sUv7rlGvgw+pq1FBO4h\nyf1gY+SbDfWaTGG+svHOVaL7r6FiQFqMBvIByzhN+n1/TNuCGYAjoCLtp6ASL0VO\ng90S0MlLTHasDPnb6PIsva5a2wKBgQDWQlCvYOkcJAoq0Sh6v4xhFP0FekM1VAhB\n4pr6bfJOn1k2VTygKHLCepifQKLgneQMCBKLoVQjAj4OAC1c9yMO/zKl2ev4ABui\ni6RfFQ8OmbbHbLWrlq09CBQrGV+7WuHL0qx5M1lF0INX2PaR0HxWY55qmVDecy8w\njpuaoWjcAwKBgGnWnM9AEtWIw1k/jyBHlOX3bx6+KhMRSjV7UBJ+BoTn0fnSTqeJ\nlK3OI+W+E8sRKzQsRRnO2ya16L571KgXxIDwjghripvLvG2kV+EdMYmWVoiE67G1\ntZGbgMRnFm4/+LKwIGWBvbSUUwPGfrtWek9mz0skJPj63hxTPKRSwsCnAoGAHXqo\nUUj7KcUHpRZ8BE+AiAb0PSGyR48VR8Ne4V/pO8oO4zvdCIgoKfvmLdsdzdvLeaBO\ntOlwgxSW5yQ9GZJjP3f7Rvhx0ABrzPR7nB1woeiiTlP1tvMXSNNouvlVw5hggsOs\nuUxIVyO2Por6edt+kABK1o3bo4+jiYHFhQP6QnMCgYBT/YDZ5bEKPUURl2fZ7bgq\n1KMm8515CM+Q2ANn54DNGz8rTQ6WSMU1F40AWdgz50mNcqQnYoepps19xNx/DLFn\nlFXvalbkFeNSX1lOn2OiV0UzXZPaaruIoKLEAyQehGGNUGbHXeNQKo+PDZsSmee0\nJxMSSB8ZrvEznTe05WyZYA==\n-----END PRIVATE KEY-----\n",
            "client_email": "email-manager@email-manager-445502.iam.gserviceaccount.com",
            "client_id": "107502812982350942334",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/email-manager%40email-manager-445502.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
            
            },
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