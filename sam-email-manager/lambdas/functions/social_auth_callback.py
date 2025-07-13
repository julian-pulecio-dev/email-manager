import json
import boto3
import os
from urllib3 import PoolManager
from urllib.parse import urlencode
from src.decorators.lambda_decorator import LambdaDecorator
from src.requests.social_auth_callback_request import SocialAuthCallbackRequest

client = boto3.client('cognito-idp', region_name='us-east-1')

EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN = os.environ.get("EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN")
EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID = os.environ.get("EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID")
CALLBACK_URL = os.environ.get("CALLBACK_URL")

@LambdaDecorator(request_class=SocialAuthCallbackRequest)
def lambda_handler(event_request: SocialAuthCallbackRequest, context):
    print("Received event:", event_request)
    code = event_request.code

    token_url = f"https://{EMAIL_MANAGER_AUTH_USER_POOL_DOMAIN}/oauth2/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": EMAIL_MANAGER_AUTH_USER_POOL_CLIENT_ID,
        "code": code,
        "redirect_uri": CALLBACK_URL
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    http = PoolManager()

    body = urlencode(payload).encode('utf-8')

    response = http.request(
        'POST',
        token_url,
        body=body,
        headers=headers
    )

    response = json.loads(response.data.decode('utf-8'))

    return {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        'Access-Control-Allow-Credentials': True
    },
    "body": json.dumps({
        'idToken': response.get('id_token'),
        'accessToken': response.get('access_token'),
        'refreshToken': response.get('refresh_token'),
        'expiresIn': response.get('expires_in'),
        'tokenType': response.get('token_type')
    })
}
