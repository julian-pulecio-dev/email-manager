from ast import In
import os
import json
import logging
from src.utils.headers import get_headers
from src.models.cognito_user_pool import CognitoUserPool
from src.models.sqs_queue import SQSQueue

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

def lambda_handler(event, context):

    cognito_user_pool = CognitoUserPool(id=os.getenv("EMAIL_MANAGER_AUTH_USER_POOL_ID"))
    users = [user.to_dict() for user in cognito_user_pool.get_users()]
    sqs_queue = SQSQueue(id="email-manager-queue")
    for user in users:
        sqs_queue.send_message(message=json.dumps(user), queue_url=SQS_QUEUE_URL)

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({
            "message": f"Scheduled processing for {len(users)} users.",
            "users": users
        })
    }
