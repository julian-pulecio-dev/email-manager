import os
import json
import logging
from base64 import b64decode
from src.decorators.event_parser import EventParser
from src.event_requests.recieve_email_request import ReceiveEmailRequest
from src.models.gmail_client import GmailClient
from src.models.dynamo_db import DynamoDBTable
from src.utils.headers import get_headers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=ReceiveEmailRequest)
def lambda_handler(event:ReceiveEmailRequest, context):
    logger.info(f'event: {event}')

    dynamo_db = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    dynamo_item = dynamo_db.get_item('email',event.email_address)

    gmail_client = GmailClient(
        google_oauth_access_token=dynamo_item.get('access_token', ''),
        google_oauth_refresh_token=dynamo_item.get('refresh_token', ''),
    )

    last_stored_history = gmail_client.retrieve_user_history_id(event.email_address)
    history = gmail_client.get_messages_from_history(last_stored_history.get('history_id', ''))
    logger.info(f'History retrieved: {history}')

    gmail_client.store_user_history_id(event.email_address, gmail_client.get_last_history_id())

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({"message": "Email received successfully"})
    }

