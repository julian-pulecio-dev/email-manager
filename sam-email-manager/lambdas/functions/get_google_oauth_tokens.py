import os
import json
import logging
from src.utils.headers import get_headers
from src.decorators.event_parser import EventParser
from src.event_requests.get_google_oauth_tokens_requests import GetGoogleOAuthTokensRequest
from src.models.google_oauth import GoogleOAuth
from src.models.dynamo_db import DynamoDBTable

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
    
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": 'success'
    }
