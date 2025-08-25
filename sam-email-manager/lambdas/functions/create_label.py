import os
import json
import logging
from src.decorators.event_parser import EventParser
from src.event_requests.create_label_request import CreateLabelRequest
from src.models.dynamo_db import DynamoDBTable
from src.models.gmail_label import GmailLabel
from src.utils.headers import get_headers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=CreateLabelRequest)
def lambda_handler(event:CreateLabelRequest, context):
    google_access_table = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    google_access_item = google_access_table.get_item('email',event.user)
    
    gmail_label = GmailLabel(
        google_oauth_access_token=google_access_item.get('access_token', ''),
        google_oauth_refresh_token=google_access_item.get('refresh_token', '')
    )
    label_id = gmail_label.create_label(event.title).get('id')

    custom_labels_table = DynamoDBTable(table_name=os.environ["GMAIL_CUSTOM_LABELS_TABLE_NAME"])
    custom_labels_table.put_item(item={"title": event.title, "instruction": event.instruction, "email": event.user, "label_id": label_id})

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({"message": "Label created successfully"})
    }

