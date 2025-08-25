import os
import json
import logging
from src.decorators.event_parser import EventParser
from src.event_requests.create_label_request import CreateLabelRequest
from src.models.dynamo_db import DynamoDBTable
from src.utils.headers import get_headers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=CreateLabelRequest)
def lambda_handler(event:CreateLabelRequest, context):
    dynamo_db_table = DynamoDBTable(table_name=os.environ["GMAIL_CUSTOM_LABELS_TABLE_NAME"])
    dynamo_db_table.put_item(item={"title": event.title, "instruction": event.instruction, "email": event.user})

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({"message": "Label created successfully"})
    }

