import boto3
import os

AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN=os.environ.get("AWS_SESSION_TOKEN")
TABLE_NAME=os.environ.get("TABLE_NAME","acm_cars")

session=boto3.Session()
client = session.client(
    'dynamodb',
    )

dynamodb = session.resource(
    'dynamodb'
    )




carTable = dynamodb.Table(TABLE_NAME)
print(carTable.creation_date_time)
carTable.put_item(
   Item={
     "car_id": "1",
     "type": "Model_1", 
     "latitude": "37.7", 
     "longitude": "-122.42",
     "status": "Available",
     "nb_passenger":  0
   })


carTable.put_item(
   Item={
     "car_id": "2",
     "type": "Model_1", 
     "latitude": "37.7", 
     "longitude": "-122.42",
     "status": "InCourse",
     "nb_passenger":  3
   })


carTable.put_item(
   Item={
     "car_id": "3",
     "type": "Model_1", 
     "latitude": "37.7", 
     "longitude": "-122.42",
     "status": "InCourse",
     "nb_passenger":  1
   })