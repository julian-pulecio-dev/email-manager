from ast import In
import os
import json
import logging
from src.utils.headers import get_headers
from src.decorators.event_parser import EventParser
from src.event_requests.send_email_request import SendEmailRequest
from src.models.dynamo_db import DynamoDBTable
from src.models.vertex_ia import VertexIA
from src.models.gmail_email import GmailEmail

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INSTRUCTION_PROMPT = """
    You interpret an email assistant. From the following text, generate a dictionary and ONLY a dictionary (with out the json word) that represents the author's desired email.
    The dictionary must have the following format:
    {{
        "interpretation_status": "success", # Indicates if the prompt was successfully interpreted
        "to": "<email_address>",
        "subject": "<email_subject>",
        "body": "<email_body>"
    }}
    If the prompt does not contain an email address, subject, or body, return an empty string for that field.
    The body must be a extense and detailed email body with at least 100 words, not just a short message unless the user explicitly asks for a brief response.
    Do not provide a text that the user must modify, fill all the information by yourself.
    If the prompt is not clear, or is not related to an email ask the user for clarification following this format:
    {{
        "interpretation_status": "clarification_needed",
        "clarification_message": "<Your clarification question>"
    }}
    return only the interpretation of the prompt, do not include any additional text.
    The user prompt may not follow the exact format, so you should be able to extract the information from a natural language prompt if possible.
    For example, if the user prompt is: "I need to send an email to john @example.com to schedule a meeting tomorrow at 10 AM.'",
    the response should be:
    {{
        "interpretation_status": "success",
        "to": "john@example.com",
        "subject": "Meeting",
        "body": "Let's meet tomorrow at 10 AM."
    }}
    For example, if the user prompt is: "I need to send an email to john@example.com to ask him about the interview.",
    the response should be:
    {{
        "interpretation_status": "success",
        "to": "john@example.com",
        "subject": "Interview Update",
        "body": "I wanted to follow up on my interview and see if there are any updates."
    }}
    For example, if the user prompt is: "I need to send an email to julia to ask her about the project status.",'",
    the response should be:
    {{
        "interpretation_status": "clarification_needed",
        "clarification_message": "can you provide the email address of julia?"
    }}
    the user prompt is: {prompt}"""

@EventParser(request_class=SendEmailRequest)
def lambda_handler(event:SendEmailRequest, context):
    dynamo_db = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    dynamo_item = dynamo_db.get_item('email',event.user)
    
    vertex_ia = VertexIA(
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
        project_id='email-manager-467721',
        location='us-central1',
        model_id='gemini-2.0-flash-lite-001'
    )

    response = vertex_ia.call_vertex(INSTRUCTION_PROMPT.format(prompt=event.prompt), files=event.attachments)

    email = GmailEmail(
        to=response.get('to', ''),
        subject=response.get('subject', ''),
        body=response.get('body', ''),
        google_oauth_access_token=dynamo_item.get('access_token', ''),
        google_oauth_refresh_token=dynamo_item.get('refresh_token', ''),
        attachments=event.attachments
    )
    
    result = email.send()
    
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps(result)
    }
