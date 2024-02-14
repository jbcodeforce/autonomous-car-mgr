import pytest

from contextlib import contextmanager
from moto import mock_aws

TABLE_NAME="test_cars"

@contextmanager
def create_table(dynamodb_client):
    """Create mock DynamoDB table to test full CRUD operations"""

    dynamodb_client.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'car_id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'car_id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    yield

@mock_aws
class TestCars:
    """Test CRUD operations on mock DynamoDB table"""

    def test_create_table(self, dynamodb_client):
        with create_table(dynamodb_client):

            res = dynamodb_client.describe_table(TableName=TABLE_NAME)
            res2 = dynamodb_client.list_tables()

            assert res['Table']['TableName'] == TABLE_NAME
            assert res2['TableNames'] == [TABLE_NAME]

    def test_put_item(self, dynamodb_client):
            dynamodb_client.put_item(
                TableName=TABLE_NAME,
                Item={"car_id": {"S":"1"}, "model": {"S":"Model_1"}, "status": {"S":"Free"}}
            )
            
            resp=dynamodb_client.get_item(
                TableName=TABLE_NAME,
                Key={"car_id": {"S":"1"}})
            
            assert resp['Item']['model']['S'] == 'Model_1'

    def test_delete_table(self, dynamodb_client):
            dynamodb_client.delete_table(TableName=TABLE_NAME)

            res = dynamodb_client.list_tables()

            assert res['TableNames'] == []