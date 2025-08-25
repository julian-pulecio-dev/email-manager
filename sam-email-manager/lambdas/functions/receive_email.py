import os
import json
import logging
from base64 import b64decode
from src.decorators.event_parser import EventParser
from src.event_requests.recieve_email_request import ReceiveEmailRequest
from src.models.gmail_client import GmailClient
from src.models.dynamo_db import DynamoDBTable
from src.models.vertex_ia import VertexIA
from src.utils.headers import get_headers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INSTRUCTION_PROMPT = """
    From the following email, classify it into zero or more of the given categories.
    Respond ONLY with a valid JSON dictionary in this exact format:
    {{
        "interpretation_status": "success",
        "labels": ["<label1>", "<label2>", ...]
    }}

    Rules:
    - Always include both keys.
    - If no category matches, return "labels": [].
    - Do not include any text, comments, or code block markers.
    - Match categories by analyzing subject, body, sender, or metadata.
    - Example:
    Email:
    {{
        "body_plain": "the latest match results are in and the teams are preparing for the next game",
        "subject": "football news",
        "from": "football@example.com",
        "date": "Sat, 23 Aug 2025 20:44:13 -0500"
    }}
    Categories:
    {{
        "football": "emails with a football theme",
        "night": "emails sent on the night",
        "weather": "emails about the weather",
        "economy": "emails about the economy"
    }}
    Expected response:
    {{
        "interpretation_status": "success",
        "labels": ["football", "night"]
    }}

    Email: {email}
    Categories: {categories}
    """
@EventParser(request_class=ReceiveEmailRequest)
def lambda_handler(event:ReceiveEmailRequest, context):
    logger.info(f'event: {event}')

    google_access_table = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    google_access_item = google_access_table.get_item('email',event.email_address)

    gmail_client = GmailClient(
        google_oauth_access_token=google_access_item.get('access_token', ''),
        google_oauth_refresh_token=google_access_item.get('refresh_token', ''),
    )

    last_stored_history = gmail_client.retrieve_user_history_id(event.email_address)
    gmail_messages = gmail_client.get_messages_from_history(last_stored_history.get('history_id', ''))
    logger.info(f'Gmail messages retrieved: {gmail_messages}')

    gmail_client.store_user_history_id(event.email_address, gmail_client.get_last_history_id())

    custom_labels_table = DynamoDBTable(table_name=os.environ['GMAIL_CUSTOM_LABELS_TABLE_NAME'])
    custom_labels = custom_labels_table.scan_items('email', event.email_address)

    categories = {lbl['title']: lbl['instruction'] for lbl in custom_labels}

    logger.info(f'Custom labels retrieved: {categories}')

    messages = []
    for gmail_message in gmail_messages:
        for message in gmail_message.messages_added:
            messages.append(message)

    responses = []
    for message in messages:
        email = {
            "body_plain": message.body_plain,
            "subject": message.subject,
            "from": message.sender,
            "date": message.date
        }

        vertex_ia = VertexIA(
            scopes=['https://www.googleapis.com/auth/cloud-platform'],
            project_id='email-manager-467721',
            location='us-central1',
            model_id='gemini-2.0-flash-lite-001'
        )

        logger.info(f'INSTRUCTION_PROMPT: {INSTRUCTION_PROMPT.format(email=json.dumps(email), categories=json.dumps(categories))}')
    

        responses.append(vertex_ia.call_vertex(INSTRUCTION_PROMPT.format(email=json.dumps(email), categories=json.dumps(categories))))

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({"message": "Email received successfully", "responses": responses})
    }

