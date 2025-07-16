import json
import logging
from src.decorators.event_parser import EventParser
from src.event_requests.social_auth_callback_request import SocialAuthCallbackRequest
from src.models.social_auth.social_auth import SocialAuth
from src.utils.headers import get_headers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@EventParser(request_class=SocialAuthCallbackRequest)
def lambda_handler(event_request: SocialAuthCallbackRequest, context):
    social_auth = SocialAuth()
    response = social_auth.get_access_tokens(
        code=event_request.code,
        provider=event_request.provider
    )
    logger.info(f"Access tokens received: {response}")
    return {
        "statusCode": 200,
        "headers": get_headers(),
        "body": json.dumps(response)
    }
