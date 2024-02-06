from aws_lambda_powertools.event_handler import APIGatewayRestResolver

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
import os
import boto3

app = APIGatewayRestResolver()
logger = Logger("ACR-mgr")
tracer = Tracer(service="ACR-mgr")

CAR_TABLE=os.environ['CAR_TABLE']
dynamodb=boto3.client('dynamodb')

@app.get("/cars/<car_id>")
@tracer.capture_method
def getCarGivenItsID(car_id):
    tracer.put_annotation(key="Car", value=car_id)
    logger.info(f"Request from {car_id} received")
    return {"message": f"Car {car_id}!"}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@tracer.capture_lambda_handler
def handler(event, context):
    return app.resolve(event, context)


# define a function to get a car from dynamodb
def getCar(car_id):
    car = dynamodb.get_item(TableName=CAR_TABLE, Key={'car_id': {'S': car_id}})
    return car