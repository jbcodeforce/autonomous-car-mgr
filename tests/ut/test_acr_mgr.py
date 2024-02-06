import json

import carmgr.app as app


class TestCarMgr:

    def test_shouldGetFirstCarByUsingId(self):
        evt={}
        evt['httpMethod']="GET"
        evt["pathParameters"]={"car_id":"1"}
        aCar= app.handler(event=evt, context={})
        assert aCar != None
        assert aCar['status'] == "Free"

    def test_shouldCreateANewCar(self):
        evt={}
        evt['httpMethod']="POST"
        carIn= {"car_id":"3", "type": "Model_2", "latitude": "37.71", "longitude": "-122.40", "status": "Free","nb_passenger":  0}
        evt["body"]=json.dumps(carIn)
        aCar= app.handler(event=evt, context={})
        assert aCar != None
        assert "created" in aCar['message']
