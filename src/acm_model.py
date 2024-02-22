from pydantic import BaseModel
from datetime import datetime

class AutonomousCar(BaseModel):
    car_id: str=None
    model: str
    year: int
    status: str
    latitude: str=None
    longitude: str=None
    nb_passengers: int=0
    bike_rack: bool=False
    created_at: datetime=None
    updated_at: datetime=None

class AutonomousCarEvent(BaseModel):
    car_id: str
    model: str
    year: int
    status: str
    latitude: str=None
    longitude: str=None
    nb_passengers: int=0
    bike_rack: bool=False
    event_type: str=None
    event_source: str=None
    event_version: str=None
    
    def fromAutonomousCar(aCar: AutonomousCar, eventType: str):
        carEvent = AutonomousCarEvent(
            car_id=aCar.car_id,
            model=aCar.model,
            year=aCar.year,
            status=aCar.status,
            nb_passengers=aCar.nb_passengers,
            event_type = eventType,
            event_source="acs.acm",
            event_version="1.0"
        )
        if aCar.latitude != None:
            carEvent.latitude = aCar.latitude
        if aCar.bike_rack != None:
            carEvent.bike_rack = aCar.bike_rack
        if aCar.longitude != None:
            carEvent.longitude = aCar.longitude
        return carEvent