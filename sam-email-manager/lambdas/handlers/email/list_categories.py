import os
import json
import logging
from src.utils.headers import get_headers
from src.decorators.event_parser import EventParser
from src.event_requests.list_labels_request import ListLabelsRequest
from src.models.dynamo_db import DynamoDBTable
from src.models.gmail_label import GmailLabel

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=ListLabelsRequest)
def lambda_handler(event:ListLabelsRequest, context):
    dynamo_db = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    dynamo_item = dynamo_db.get_item('email',event.user)

    gmail_label = GmailLabel(dynamo_item.get('access_token'),dynamo_item.get('refresh_token'))
    labels = gmail_label.get_labels()

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps(labels)
    }
