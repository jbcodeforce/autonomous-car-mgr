
from aws_lambda_powertools import Logger
logger = Logger()
import datetime


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

    def updateCar(self, car: dict):
        car['updated_at'] = datetime.datetime.now().isoformat()
        logger.debug(car)
        carOut = self.table.put_item( Item=car)
        return carOut
    
    def deleteCar(self, car_id: str):
        car = self.table.delete_item( Key={"car_id": car_id})
        return car

