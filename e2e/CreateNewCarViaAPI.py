import requests,json

if __name__ == '__main__':

    carJson={"nb_passengers":"4",
             "car_id":"5",
             "model":"Model_2",
             "year":"2024",
             "longitude":"-122.42",
             "status":"Available",
             "bike_rack": True,
             "latitude":"37.7"}
    # post to an api using requests
    resp=requests.post('https://dcoy1ihhwa.execute-api.us-west-2.amazonaws.com/dev/cars/', 
                  json=carJson,
                  headers={"Content-Type": "application/json"})
    print(resp.json())