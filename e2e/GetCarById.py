import boto3
import argparse


session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('acm_cars')
client = session.client(
    'dynamodb',
    )


# access car by id from dynamodb car_table
def get_car(id):
    
    response = table.get_item(Key={'car_id': id})
    return response['Item']

# parse argument to get car id
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    for t in client.list_tables()['TableNames']:
        print(t)

    car = get_car(args.id)
    print(car)
    print(f"Car {args.id} is {car['type']} at {car['latitude']}, {car['longitude']}")
