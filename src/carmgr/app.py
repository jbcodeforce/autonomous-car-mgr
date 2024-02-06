
import os
import boto3,json


CAR_TABLE=os.environ.get('CAR_TABLE_NAME',"acm_cars")
dynamodb=boto3.resource('dynamodb')
car_table=dynamodb.Table(CAR_TABLE)


def handler(event, context):
    print(event)
    httpMethod = event['httpMethod']
    if httpMethod == 'GET':
        car_id = event['pathParameters']['car_id']
        car = getCar(car_id)
        return car
    elif httpMethod == 'POST':
        carStr=event['body']
        car=json.loads(carStr)
        carOut = createCar(car)
        print(carOut)
        return {"message": "Car created successfully"}
    else:
        return {'error': 'Invalid HTTP method'}



# define a function to get a car from dynamodb
def getCar(car_id):
    car = car_table.get_item( Key={'car_id': car_id})
    print(car)
    return car['Item']

def createCar(car):
    carOut = car_table.put_item( Item=car)
    return carOut