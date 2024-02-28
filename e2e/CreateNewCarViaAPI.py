import requests,json,os,random,argparse

API_GTW=os.getenv('API_GTW')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    carJson={"nb_passengers":"4",
             "car_id": args.id,
             "model":"Model_" + str(random.randint(1,5)),
             "year":"202" + str(random.randint(3,4)),
             "longitude":"-122.42",
             "status": "Available",
             "bike_rack": (True if random.randint(1,50) > 25 else False),
             "latitude": "37.7"}
    # post to an api using requests
    print(f"Posting to {API_GTW}/cars/ the cars {carJson}")
    
    resp=requests.post(API_GTW+'/cars/', 
                  json=carJson,
                  headers={"Content-Type": "application/json"})
    print(resp.json())
    