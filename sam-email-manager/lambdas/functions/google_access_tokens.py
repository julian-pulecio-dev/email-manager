import os
import json
import logging
from src.utils.headers import get_headers
from src.decorators.event_parser import EventParser
from src.event_requests.get_google_oauth_tokens_requests import GetGoogleOAuthTokensRequest
from src.models.google_oauth import GoogleOAuth
from src.models.dynamo_db import DynamoDBTable
from src.models.gmail_watch import GmailWatch
from src.models.gmail_client import GmailClient


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=GetGoogleOAuthTokensRequest)
def lambda_handler(event:GetGoogleOAuthTokensRequest, context):
    google_auth = GoogleOAuth(
        client_id=os.environ['GOOGLE_CLIENT_ID'],
        client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
        redirect_uri='http://localhost:5173/google-oauth-confirm-code'
    )
    access_tokens = google_auth.exchange_code_for_tokens(event.code)
    dynamo_db = DynamoDBTable(table_name=os.environ['GOOGLE_OAUTH_ACCESS_TOKENS_TABLE_NAME'])
    dynamo_db.put_item(access_tokens.to_dict())
    gmail_history = GmailClient(
        google_oauth_access_token=access_tokens.access_token,
        google_oauth_refresh_token=access_tokens.refresh_token
    )

    last_history_id = gmail_history.get_last_history_id()
    gmail_history.store_user_history_id(event.user, last_history_id)

    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": 'success'
    }
