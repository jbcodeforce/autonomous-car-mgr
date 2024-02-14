import carmgr.acm_model as acm_model
import json 
from pydantic.json import pydantic_encoder


def test_car_serialization():
    aCar = acm_model.AutonomousCar(car_id="car01",
                year= 2024,
                model= "Model_1",
                status= "Available"
                )                  
    print(aCar)
    outCar=aCar.model_dump_json()
    assert outCar == '{"car_id":"car01","model":"Model_1","year":2024,"status":"Available","latitude":null,"longitude":null,"nb_passengers":0,"bike_rack":false,"created_at":null,"updated_at":null}'
    outCar=json.dumps(aCar, default=pydantic_encoder)
    print(outCar)
    assert outCar == '{"car_id": "car01", "model": "Model_1", "year": 2024, "status": "Available", "latitude": null, "longitude": null, "nb_passengers": 0, "bike_rack": false, "created_at": null, "updated_at": null}'
    

def test_car_deserialization():
    newCar=acm_model.AutonomousCar.model_validate_json('{"car_id":"car02","model":"Model_2","year":2024,"status":"Available"}')
    assert newCar.model == "Model_2"


def test_createEvent():
    aCar = acm_model.AutonomousCar(car_id="XXXXX",
                year= 2024,
                model= "Model_1",
                status= "Available",
                nb_passengers=0,
                )
    aEvent = acm_model.AutonomousCarEvent.fromAutonomousCar(aCar)
    assert aEvent.status == "Available"
    

def test_car_to_dict():
    aCar = acm_model.AutonomousCar(car_id="XXXXX",
                year= 2024,
                model= "Model_1",
                status= "Available",
                nb_passengers=0,
                )
    aDict = aCar.model_dump()
    assert aDict['car_id'] == "XXXXX"
    assert aDict['model'] == "Model_1"
    assert aDict['year'] == 2024
    assert aDict['status'] == "Available"
    assert aDict['nb_passengers'] == 0

def test_car_from_dict():
    aDict = {"car_id":"XXXXX",
                "year": 2024,
                "model": "Model_1",
                "status": "Available",
                "nb_passengers":0,
                }
    aCar = acm_model.AutonomousCar.model_validate(aDict)
    assert aCar.model == "Model_1"