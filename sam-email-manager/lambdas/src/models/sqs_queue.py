import logging
from boto3 import client
import botocore
from dataclasses import dataclass, field
from src.exceptions.server_exception import ServerException


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class SQSQueue:
    id: str
    boto3_client: object = field(default_factory=lambda: client('sqs'))

    def send_message(self, message: str, queue_url: str) -> dict:
        try:
            response = self.boto3_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message
            )
            return response
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error sending message to SQS: {e}")
            raise ServerException("Error sending message to SQS")
        
    def receive_messages(self, queue_url: str, max_number: int = 1) -> list[dict]:
        try:
            response = self.boto3_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_number
            )
            return response.get('Messages', [])
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error receiving messages from SQS: {e}")
            raise ServerException("Error receiving messages from SQS")
