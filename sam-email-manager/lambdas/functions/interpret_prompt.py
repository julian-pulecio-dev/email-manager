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
    logger.info(f'event headers: {json.dumps(event.headers)}')
    dynamo_db = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    logger.info(f'request user {event.user}')
    dynamo_item = dynamo_db.get_item('email',event.user)
    logger.info(f'dynamo item: {dynamo_item}')
    vertex_ia = VertexIA(
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
        project_id='email-manager-445502',
        location='us-central1',
        model_id='gemini-2.0-flash-lite-001'
    )
    response = vertex_ia.call_vertex(event.prompt)
    logger.info(f'response vertex_ia : {response}')
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps(response)
    }
