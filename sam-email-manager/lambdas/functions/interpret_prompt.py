import os
import json
import logging
from src.utils.headers import get_headers
from src.decorators.event_parser import EventParser
from src.event_requests.interpret_prompt_request import InterpretPromptRequest
from src.models.dynamo_db import DynamoDBTable
from src.models.vertex_ia import VertexIA

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=InterpretPromptRequest)
def lambda_handler(event:InterpretPromptRequest, context):
    dynamo_db = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    dynamo_item = dynamo_db.get_item('email',event.user)
    vertex_ia = VertexIA(
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
        project_id='email-manager-445502',
        location='us-central1',
        model_id='gemini-2.0-flash-lite-001'
    )
    response = vertex_ia.call_vertex(event.prompt)
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps(response)
    }
