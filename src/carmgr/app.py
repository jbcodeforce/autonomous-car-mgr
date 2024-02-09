
import os
import boto3,json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit


CAR_TABLE=os.environ.get("CAR_TABLE_NAME","acm_cars")
POWERTOOLS_METRICS_NAMESPACE=os.environ.get("POWERTOOLS_METRICS_NAMESPACE", "Powertools")
app = APIGatewayRestResolver()  # proxy_type=ProxyEventType.APIGatewayProxyEvent
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace=POWERTOOLS_METRICS_NAMESPACE)





dynamodb=boto3.resource('dynamodb')
car_table=dynamodb.Table(CAR_TABLE)

@app.get("/cars")
@tracer.capture_method
def getAllCars():
    cars = car_table.scan()
    return cars['Items']

@app.get("/cars/<car_id>")
@tracer.capture_method
def getCarUsingCarId(car_id: str):
    car = car_table.get_item( Key={'car_id': car_id})
    logger.debug(car)
    return car['Item']

@app.post("/cars")
def createCar():
    car: dict = app.current_event.json_body 
    carOut = car_table.put_item( Item=car)
    return carOut

# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)




