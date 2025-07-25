import logging
from boto3 import client
import botocore
from dataclasses import dataclass, field
from src.exceptions.server_exception import ServerException


logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class DynamoDBTable:
    table_name: str
    boto3_client: object = field(default_factory=lambda: client('dynamodb'))

    def put_item(self, item: dict):
        try:
            item = DynamoDBItem.from_dict(item)
            logger.info(f'Put item into DynamoDB: {item}')
            return self.boto3_client.put_item(TableName=self.table_name, Item=item)
        except (ValueError, botocore.exceptions.ClientError) as e:
            raise ServerException(str(e))

    def get_item(self, key_name: str, key_value, key_type: str = 'S'):
        try:
            key = {key_name: {key_type: str(key_value)}}
            response = self.boto3_client.get_item(TableName=self.table_name, Key=key)
            item = response.get("Item")
            return DynamoDBItem.to_dict(item) if item else None
        except (ValueError, botocore.exceptions.ClientError) as e:
            raise ServerException(str(e))


class DynamoDBItem:
    @classmethod
    def from_dict(cls, dict_item: dict):
        if not isinstance(dict_item, dict):
            raise ValueError(f'{dict_item} param must be a dictionary')

        dynamo_db_item = {}
        for key, value in dict_item.items():
            value_type = cls.get_item_value_type(value)

            if value_type == 'M':
                item_value = {value_type: cls.from_dict(value)}
            elif value_type == 'L':
                item_value = {
                    value_type: [
                        cls.from_dict(v) if isinstance(v, dict)
                        else {cls.get_item_value_type(v): str(v) if isinstance(v, (int, float)) else v}
                        for v in value
                    ]
                }
            elif value_type == 'N':
                item_value = {value_type: str(value)}
            else:
                item_value = {value_type: value}

            dynamo_db_item[key] = item_value

        return dynamo_db_item

    @classmethod
    def get_item_value_type(cls, value):
        if isinstance(value, str):
            return 'S'
        if isinstance(value, (int, float)):
            return 'N'
        if isinstance(value, bytes):
            return 'B'
        if isinstance(value, dict):
            return 'M'
        if isinstance(value, list):
            return 'L'
        if isinstance(value, set):
            return cls.handle_set(value)
        raise ValueError(f'Unhandled type: {type(value)}')

    @classmethod
    def handle_set(cls, value: set):
        if not value:
            raise ValueError('The set cannot be empty')

        types = {type(v) for v in value}
        if len(types) > 1:
            raise ValueError('Set must contain elements of the same type')

        elem_type = cls.get_item_value_type(next(iter(value)))
        if elem_type not in ['S', 'N', 'B']:
            raise ValueError('Only sets of strings, numbers, or binaries are supported')
        return elem_type + 'S'

    @classmethod
    def to_dict(cls, dynamodb_item: dict):
        if not isinstance(dynamodb_item, dict):
            raise ValueError(f'{dynamodb_item} param must be a dictionary')

        plain_dict = {}
        for key, value in dynamodb_item.items():
            plain_dict[key] = cls._parse_dynamo_value(value)
        return plain_dict

    @classmethod
    def _parse_dynamo_value(cls, value: dict):
        if not isinstance(value, dict) or len(value) != 1:
            raise ValueError(f'Invalid DynamoDB value: {value}')

        type_key, actual_value = next(iter(value.items()))

        if type_key == 'S':
            return actual_value
        if type_key == 'N':
            return int(actual_value) if actual_value.isdigit() else float(actual_value)
        if type_key == 'B':
            return actual_value  # puede depender si es base64
        if type_key == 'M':
            return cls.to_dict(actual_value)
        if type_key == 'L':
            return [cls._parse_dynamo_value(i) for i in actual_value]
        if type_key == 'SS':
            return set(actual_value)
        if type_key == 'NS':
            return {int(v) if v.isdigit() else float(v) for v in actual_value}
        if type_key == 'BS':
            return set(actual_value)
        raise ValueError(f'Unhandled DynamoDB type: {type_key}')
