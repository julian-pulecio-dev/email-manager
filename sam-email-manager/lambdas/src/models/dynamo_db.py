import logging
from boto3 import client
import botocore
from dataclasses import dataclass, field
from src.exceptions.server_exception import ServerException



logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass
class DynamoDBTable:
    table_name:str
    boto3_client:object = field(default_factory=lambda : client('dynamodb'))
    
    def put_item(self, item:dict):
        try:
            item = DynamoDBItem.from_dict(item)
            logger.info(f'dynamo item: {item}')
            response = self.boto3_client.put_item(
                TableName = self.table_name,
                Item = item
            )
            return response
        except ValueError as e:
            raise ServerException(str(e))
        except botocore.exceptions.ClientError as error:
            raise ServerException(str(error))

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
            elif value_type == 'N':
                item_value = {value_type: str(value)}
            elif value_type == 'L':
                item_value = {value_type: [
                    cls.from_dict(v) if isinstance(v, dict)
                    else {cls.get_item_value_type(v): str(v) if isinstance(v, int) else v}
                    for v in value
                ]}
            else:
                item_value = {value_type: value}
            dynamo_db_item[key] = item_value

        return dynamo_db_item

    @classmethod
    def get_item_value_type(cls, value: any):
        if isinstance(value, str):
            return 'S'
        if isinstance(value, int):
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
            raise ValueError('The set must contain elements of the same type')
        elem_type = cls.get_item_value_type(next(iter(value)))
        if elem_type not in ['S', 'N', 'B']:
            raise ValueError('Only sets of string, number, or binary are allowed')
        return elem_type + 'S'