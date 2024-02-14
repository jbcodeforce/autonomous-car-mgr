import os
import pytest
from boto3 import resource
from contextlib import contextmanager
from moto import mock_aws
import json
from pathlib import Path
from typing import Any
import carmgr.app as app


TABLE_NAME="test_cars"
EVENT_BUS="test_event_bus"

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
    dynamodb_client.delete_table(TableName=TABLE_NAME)

@pytest.fixture(scope="module")
def populate_table(dynamodb_client):
    with create_table(dynamodb_client):
        dynamodb_client.put_item(
            TableName=TABLE_NAME,
            Item={"car_id": {"S":"1"}, "model": {"S":"Model_1"}, "status": {"S":"Free"}}
        )
        dynamodb_client.put_item(
            TableName=TABLE_NAME,
            Item={"car_id": {"S":"2"}, "model": {"S":"Model_2"}, "status": {"S":"Free"}}
        )
        yield

@pytest.fixture(scope="module")
def getApp(dynamodb_client,populate_table,event_client):
    TEST_REPOSITORY_DEFINITION = {"resource": resource('dynamodb'), 
                                 "table_name": TABLE_NAME}
    TEST_EVENT_DEFINITION = {"event_bus": EVENT_BUS}
    app.car_repository = app.CarRepository(TEST_REPOSITORY_DEFINITION)
    app.event_producer = app.CarEventProducer(TEST_EVENT_DEFINITION)
    return app

def load_event(file_name: str) -> Any:
    path = Path(str(Path(__file__).parent.parent) + "/events/" + file_name)
    return json.loads(path.read_text())

@mock_aws
class TestCarMgr:

        
    def test_shouldGetFirstCarByUsingId(self,getApp):
        aCar=getApp.getCarUsingCarId("1")
        print(aCar)
        assert aCar != None
        assert aCar['status'] == "Free"


    def test_shouldGetAllCars(self,getApp):
        allCars=getApp.getAllCars()
        print(allCars)
        assert allCars != None
        assert len(allCars) > 0


    def test_shouldCreateANewCar(self,getApp):
        apigtw_msg=load_event("postCar.json")
        body=json.loads(apigtw_msg['body'])
        print(body)
        resp = getApp.car_repository.createCar(body)
        print(resp)

    def test_shouldUpdateExistingCar(self,getApp):
        aCar=getApp.getCarUsingCarId("1")
        aCar['status']="Rented"
        print(aCar)
        resp = getApp.car_repository.updateCar(aCar)
        print(resp)

