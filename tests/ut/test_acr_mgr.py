import json
import pytest
import json
from pathlib import Path
from typing import Any
import carmgr.app as app

@pytest.fixture
def lambda_context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "test-func"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:eu-west-1:809313241234:function:test-func"
            self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

        def get_remaining_time_in_millis(self) -> int:
            return 1000

    return LambdaContext()

def load_event(file_name: str) -> Any:
    path = Path(str(Path(__file__).parent.parent) + "/events/" + file_name)
    return json.loads(path.read_text())

class TestCarMgr:

    def test_shouldGetFirstCarByUsingId(self):
        aCar=app.getCarUsingCarId("1")
        print(aCar)
        assert aCar != None
        assert aCar['status'] == "Free"

    def test_shouldGetAllCars(self):
        allCars=app.getAllCars()
        print(allCars)
        assert allCars != None
        assert len(allCars) > 0

    def test_shouldGetCarById(self,lambda_context):
        minimal_event = {
            "path": "/cars/2",
            "httpMethod": "GET",
            "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},  # correlation ID
        }
        resp = app.handler(minimal_event,lambda_context )
        print(resp)
        assert resp["statusCode"] == 200
        assert resp["body"] != ""
        aCar=json.loads(resp["body"])
        assert "Model_1" in aCar["type"]

    def test_shouldCreateANewCar(self,lambda_context):
        apigtwEvent=load_event("postCar.json")
        resp = app.handler(apigtwEvent,lambda_context )
        print(resp)
        assert resp["statusCode"] == 200
        assert resp["body"] != ""
