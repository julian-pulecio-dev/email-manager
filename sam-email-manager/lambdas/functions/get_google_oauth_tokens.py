import traceback
import os
import json
import requests
import logging
from urllib.parse import urlencode
from src.utils.headers import get_headers
from src.decorators.event_parser import EventParser
from src.event_requests.get_google_oauth_tokens_requests import GetGoogleOAuthTokensRequest
from src.models.google_oauth.google_oauth import GoogleOAuth

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=GetGoogleOAuthTokensRequest)
def lambda_handler(event:GetGoogleOAuthTokensRequest, context):
    google_auth = GoogleOAuth(
        client_id=os.environ['GOOGLE_CLIENT_ID'],
        client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
        redirect_uri='http://localhost:5173/google-oauth-confirm-code'
    )
    response = google_auth.exchange_code_for_tokens(event.code)
    logger.info(f"Access tokens received: {response}")
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps(response)
    }
