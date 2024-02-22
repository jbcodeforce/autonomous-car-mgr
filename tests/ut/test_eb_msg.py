import boto3,json
from unittest import mock
from unittest.mock import patch

import app as app

eventbridge_client = mock.Mock()
eventbridge_client.put_events.return_value = {
        'statusCode': 200,
        'body': json.dumps('Car added')
    }


def test_create_event_producer():
    with mock.patch('boto3.client') as mock_boto3_client:
        mock_boto3_client.return_value = eventbridge_client
        producer = app.CarEventProducer(app.DEFAULT_EVENT_PRODUCER)
        assert producer != None


def test_send_event_producer():
    with mock.patch('boto3.client') as mock_boto3_client:
        mock_boto3_client.return_value = eventbridge_client
        producer = app.CarEventProducer(app.DEFAULT_EVENT_PRODUCER)
        aCar=app.AutonomousCar(model="Model_2",car_id="XXXXX",status="Available",year=2024)
        rep = producer.produceCarEvent(aCar,"a.test.event")
        print(rep)
        assert rep['statusCode'] == 200 



