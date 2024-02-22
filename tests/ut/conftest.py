import os
import pytest
import json
from pathlib import Path
from typing import Any
import app as app
import boto3
import moto
from moto import mock_aws


@pytest.fixture(scope="module")
def lambda_context(aws_credentials):
    class LambdaContext:
        def __init__(self):
            self.function_name = "test-func"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:eu-west-1:809313241234:function:test-func"
            self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

        def get_remaining_time_in_millis(self) -> int:
            return 1000

    return LambdaContext()



CAR_TABLE=os.environ.get("CAR_TABLE_NAME","acm_cars")

@pytest.fixture(scope="module")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"

@pytest.fixture(scope="module")
def dynamodb_client(aws_credentials):
    """DynamoDB mock client."""
    with mock_aws():
        conn = boto3.client("dynamodb", region_name="us-west-2")
        yield conn

@pytest.fixture(scope="module")
def event_client(aws_credentials):
    with mock_aws():
        conn = boto3.client("events", region_name="us-west-2")
        yield conn

@pytest.fixture(scope="module")
def secret_client(aws_credentials):
    with mock_aws():
        conn = boto3.client("secretsmanager", region_name="us-west-2")
        yield conn