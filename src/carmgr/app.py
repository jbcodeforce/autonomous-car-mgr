
import os
import boto3,json,datetime
from boto3 import resource
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit

try:
 from .acm_model import AutonomousCar, AutonomousCarEvent
except ImportError:
    from carmgr.acm_model import AutonomousCar, AutonomousCarEvent
    
import uuid

POWERTOOLS_METRICS_NAMESPACE=os.environ.get("POWERTOOLS_METRICS_NAMESPACE", "Powertools")
app = APIGatewayRestResolver()  # proxy_type=ProxyEventType.APIGatewayProxyEvent
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace=POWERTOOLS_METRICS_NAMESPACE)

DEFAULT_REPOSITORY_DEFINITION = {"resource": resource('dynamodb'),
                                 "table_name": os.environ.get("CAR_TABLE_NAME","acm_cars")}

DEFAULT_EVENT_PRODUCER = {"event_bus": os.environ.get("CAR_EVENT_BUS","acm_cars")}


class CarRepository:
    
    def __init__(self, table_resource):
        self.table_name = table_resource["table_name"]
        self.resource = table_resource["resource"]
        self.table = self.resource.Table(self.table_name)


    def getAllCars(self):
        cars = self.table.scan()
        return cars['Items']

    def getCarUsingCarId(self, car_id: str):
        car = self.table.get_item( Key={"car_id": car_id})
        logger.debug(car)
        return car['Item']

    def createCar(self, car: dict):
        car['created_at'] = datetime.datetime.now().isoformat()
        car['updated_at'] = datetime.datetime.now().isoformat()
        logger.debug(car)
        carOut = self.table.put_item( Item=car)
        return carOut
        carOut = self.table.put_item( Item=car)
        return carOut

    def updateCar(self, car: dict):
        car['updated_at'] = datetime.datetime.now().isoformat()
        logger.debug(car)
        carOut = self.table.put_item( Item=car)
        return carOut
    
    def deleteCar(self, car_id: str):
        car = self.table.delete_item( Key={"car_id": car_id})
        return car

class CarEventProducer:
    def __init__(self, event_backbone_resource):
        self.event_backbone = boto3.client('events')
        self.event_bus = event_backbone_resource["event_bus"]

    def produceCarEvent(self, aCar: AutonomousCar, eventType: str):
        payload=AutonomousCarEvent.fromAutonomousCar(aCar=aCar,eventType=eventType)
        carEvent = {
                    'Source': 'acs.acm',
                    'DetailType': eventType, #'acme.acs.acm.events.CarUpdated',
                    'Detail': payload.model_dump_json(),
                    'EventBusName': self.event_bus
                }
        logger.info(carEvent)
        
        return self.event_backbone.put_events(
            Entries=[
                carEvent
            ]
        )


car_repository=CarRepository(DEFAULT_REPOSITORY_DEFINITION)
event_producer=CarEventProducer(DEFAULT_EVENT_PRODUCER)

# Demo code
secret_name=os.getenv("secret_name",default="ACS_secret")
region=os.getenv("AWS_DEFAULT_REGION")
session = boto3.session.Session()
secret_client=session.client(service_name="secretsmanager")
try:
        secret_value_response = secret_client.get_secret_value(
            SecretId=secret_name
        )
        logger.info(f"secret read from AWS secret {secret_value_response['username']}")
except Exception as e:
    logger.error(e)

@app.get("/cars")
@tracer.capture_method
def getAllCars():
    return car_repository.getAllCars()

@app.get("/cars/<car_id>")
@tracer.capture_method
def getCarUsingCarId(car_id: str):
    return car_repository.getCarUsingCarId(car_id=car_id)

@app.post("/cars")
def createCar():
    car: dict = app.current_event.json_body 
    if 'car_id' not in car:
        car['car_id'] = str(uuid.uuid4())
    if 'status' not in car:
        car['status'] = 'Available'
    if 'latitude' not in car or car['latitude'] == None:
        car['latitude'] = "0"
    if 'longitude' not in car or car['longitude'] == None:
        car['longitude'] = "0"
    car_repository.createCar(car)
    
    event_producer.produceCarEvent(aCar=AutonomousCar.model_validate(car), eventType="acme.acs.acm.events.CarCreated")
    return {
        'statusCode': 200,
        'body': json.dumps('Car added')
    }

@app.put("/cars/<car_id>")
def updateCar(car_id: str):
    car: dict = app.current_event.json_body 
    car['car_id'] = car_id
    car_repository.updateCar(car)
    event_producer.produceCarEvent(aCar=AutonomousCar.model_validate(car), eventType="acme.acs.acm.events.CarUpdated")  
    return {"status": "updated"}


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(message: dict, context: LambdaContext) -> dict:
    return app.resolve(message, context)




