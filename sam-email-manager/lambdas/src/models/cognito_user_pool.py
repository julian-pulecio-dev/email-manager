import logging
from dataclasses import dataclass, field
from typing import Any, List, Optional
from datetime import datetime

import botocore
from boto3 import client

from src.exceptions.server_exception import ServerException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class CognitoUserPool:
    id: str
    boto3_client: Any = field(default_factory=lambda: client("cognito-idp"))

    def get_users(self) -> List["CognitoUser"]:
        users: List[CognitoUser] = []
        pagination_token: Optional[str] = None

        while True:
            try:
                if pagination_token:
                    response = self.boto3_client.list_users(
                        UserPoolId=self.id,
                        PaginationToken=pagination_token
                    )
                else:
                    response = self.boto3_client.list_users(UserPoolId=self.id)

            except botocore.exceptions.BotoCoreError as e:
                logger.error(f"Error fetching users from Cognito: {e}")
                raise ServerException("Failed to fetch users from Cognito") from e

            users += [CognitoUser.from_dict(u) for u in response.get("Users", [])]

            pagination_token = response.get("PaginationToken")
            if not pagination_token:
                break

        return users


@dataclass
class CognitoUser:
    id: str
    email: str
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    enabled: bool
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> "CognitoUser":
        attributes = {attr["Name"]: attr["Value"] for attr in data.get("Attributes", [])}
        return cls(
            id=data.get("Username"),
            email=attributes.get("email", ""),
            name=attributes.get("name", ""),
            created_at=data.get("UserCreateDate"),
            updated_at=data.get("UserLastModifiedDate"),
            enabled=data.get("Enabled", False),
            status=data.get("UserStatus", "UNKNOWN"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "enabled": self.enabled,
            "status": self.status,
        }
