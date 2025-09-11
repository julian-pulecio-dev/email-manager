import logging
from boto3 import client
import botocore
from dataclasses import dataclass, field
from src.exceptions.server_exception import ServerException


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class CognitoUserPool:
    id: str
    boto3_client: object = field(default_factory=lambda: client('cognito-idp'))

    def get_users(self) -> list["CognitoUser"]:
        users = []
        pagination_token = None

        while True:
            if pagination_token:
                response = self.boto3_client.list_users(
                    UserPoolId=self.id,
                    PaginationToken=pagination_token
                )
            else:
                response = self.boto3_client.list_users(
                    UserPoolId=self.id
                )
            users.extend(CognitoUser.from_dict(user) for user in response.get("Users", []))

            pagination_token = response.get("PaginationToken")
            if not pagination_token:
                break
        return users

@dataclass
class CognitoUser:
    id: str
    email: str
    name: str
    created_at: str
    updated_at: str
    enabled: bool
    status: str

    @classmethod
    def from_dict(cls, data: dict):
        attributes = {attr['Name']: attr['Value'] for attr in data.get('Attributes', [])}
        return cls(
            id=data.get('Username'),
            email=attributes.get('email'),
            name=attributes.get('name'),
            created_at=data.get('UserCreateDate').isoformat() if data.get('UserCreateDate') else None,
            updated_at=data.get('UserLastModifiedDate').isoformat() if data.get('UserLastModifiedDate') else None,
            enabled=data.get('Enabled'),
            status=data.get('UserStatus')
        )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled": self.enabled,
            "status": self.status
        }
