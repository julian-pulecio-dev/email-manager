import os
import json
import logging
from src.decorators.event_parser import EventParser
from src.event_requests.sqs_queue_request import SQSQueueRequest
from src.models.gmail_client import GmailClient
from src.models.gmail_watch_dog import GmailWatchDog
from src.models.dynamo_db import DynamoDBTable
from src.models.vertex_ia import VertexIA
from src.models.gmail_label import GmailLabel
from src.utils.headers import get_headers

logger = logging.getLogger()
logger.setLevel(os.getenv("LOGGER_LEVEL", "NOTSET"))

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
    - The files attached to this prompt are the attachments of the email analize them to find relevant information.
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
@EventParser(request_class=SQSQueueRequest)
def lambda_handler(event:SQSQueueRequest, context):
    message = 'no new email found'

    google_access_table = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    google_access_item = google_access_table.get_item('email', event.email)

    gmail_client = GmailClient(
        google_oauth_access_token=google_access_item.get('access_token', ''),
        google_oauth_refresh_token=google_access_item.get('refresh_token', ''),
    )

    gmail_watch_dog = GmailWatchDog(
        google_oauth_access_token=google_access_item.get('access_token', ''),
        google_oauth_refresh_token=google_access_item.get('refresh_token', '')
    )

    last_stored_history = gmail_client.retrieve_user_history_id(event.email)

    if  not gmail_watch_dog.check_changes(last_stored_history.get('history_id', '')):
        
        message = 'no new email found'
        logger.info(message)

        return {
            "statusCode": 200,
            "headers": get_headers(),
            "body": json.dumps({"message": f"Email received successfully - {message}"})
        }        

    gmail_messages = gmail_client.get_messages_from_history(last_stored_history.get('history_id', ''))

    custom_labels_table = DynamoDBTable(table_name=os.environ['GMAIL_CUSTOM_LABELS_TABLE_NAME'])
    custom_labels = custom_labels_table.scan_items('email', event.email)

    filtered_labels = []
    for lbl in custom_labels:
        filtered_labels.extend(lbl['filtered_labels'].split(','))

    logger.debug(f'Filtered labels: {filtered_labels}')

    categories = {lbl['title']: lbl['instruction'] for lbl in custom_labels}

    logger.debug(f'Categories: {categories}')

    vertex_ia = VertexIA(
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
        project_id='email-manager-467721',
        location='us-central1',
        model_id='gemini-2.0-flash-lite-001'
    )

    gmail_label = GmailLabel(
        google_oauth_access_token=google_access_item.get('access_token', ''),
        google_oauth_refresh_token=google_access_item.get('refresh_token', '')
    )

    logger.info(f'Found {len(gmail_messages)} new emails to process')

    for message in gmail_messages:

        if  not set(message.label_ids).intersection(set(filtered_labels)):
            logger.info(f'Skipping email with ID: {message.id} - Labels: {message.label_ids} do not match filtered labels: {filtered_labels}')
            continue

        instruction =  INSTRUCTION_PROMPT.format(email=json.dumps(message.to_dict()), categories=json.dumps(categories))
            
        logger.debug(f'Instruction: {instruction}')
            
        response = vertex_ia.call_vertex(instruction, message.attachments)

        logger.info(f'IA Response: {response}')

        labels_ids = [label['label_id'] for label in custom_labels if label['title'] in response.get('labels', [])]    

        gmail_label.move_message_to_label(message.id, labels_ids, filtered_labels)

        message = f'Processed email with ID: {message.id} - Applied labels: {response.get("labels", [])}'

    gmail_client.store_user_history_id(event.email, gmail_client.get_last_history_id())
    logger.info(f'Processed {len(gmail_messages)} emails')
    
    logger.info(message)

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps({"message": f"Email received successfully - {message}"})
    }
