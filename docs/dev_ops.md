# DevOps

As solution deployed on AWS, and integrating with AWS services, developers need to study the [SDK (e.g. Python boto3 module)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html). 

## Tools to support code deployment

The core element of the infrastructure as code (IaC) on AWS is [AWS CloudFormation](https://aws.amazon.com/cloudformation). If developers or devops engineers prefer to use programming language to define service configuration and code deployment the [AWS Cloud Development Kit](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) is a powerful solution. It uses code which can be integrated in the same Git repository as application / microservice code. 

For serverless implementation, [AWS Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/) is a declarative way to define IaC, by using higher level template than CloudFormation.

CDK uses an imperative programming style which can make complex logic and conditionals easier to implement compared to the declarative style of AWS SAM templates.

SAM CLI supports local development and testing of Lambda apps, CDK provides a full-featured local development environment with watch mode.

Developer can use the AWS SAM CLI to locally test and build serverless applications defined using the AWS Cloud Development Kit (AWS CDK). [See Getting started with AWS SAM and the AWS CDK.](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-cdk-getting-started.html).


## Code boilerplate

[AWS Powertools](https://docs.powertools.aws.dev/lambda/python/) has a REST resolver to annotate function to support different REST resource paths and HTTP verbs. It leads to cleaner code, and easier to test the business logic: each path and HTTP method is implemented by different function:

```python
@app.get("/cars/<car_id>")
@tracer.capture_method
def getCarUsingCarId(car_id: str):
    car = car_table.get_item( Key={'car_id': car_id})
    logger.debug(car)
    return car['Item']
```

[See the app.py code](https://github.com/jbcodeforce/autonomous-car-mgr/blob/main/src/carmgr/app.py) and how to unit test it using pytest [test_acr_mgr.py](https://github.com/jbcodeforce/autonomous-car-mgr/blob/main/tests/ut/test_acr_mgr.py).

When using Powertools REST resolver, the API Gateway API needs to be a proxy integration to Lambda as the REST resolver will use the metadata of the request.

```python
def handler(message: dict, context: LambdaContext) -> dict:
    return app.resolve(message, context)
```

* To reuse code in more than one function, consider creating a Layer and deploying it. A layer is a ZIP archive that contains libraries, a custom runtime, or other dependencies. [See layer management in product documentation]()

### Unit testing

The unittest can be done using mock library to bypass remote calls. Tests may be defined using pytest library and commands.

For example the folder: [tests/ut](https://github.com/jbcodeforce/autonomous-car-mgr/tree/main/tests/ut) includes test case definitions to test the microservice. 

```sh
pytest -vs
```

* Example of test mock for a dynamodb client, using [moto library](https://docs.getmoto.org/en/latest/)

```python
from moto import mock_aws

@pytest.fixture(scope="module")
def dynamodb_client(aws_credentials):
    """DynamoDB mock client."""
    with mock_aws():
        conn = boto3.client("dynamodb", region_name="us-west-2")
        yield conn
```

* With injection to tune the app under test

```python
@pytest.fixture(scope="module")
def getApp(dynamodb_client,populate_table,event_client,secret_client):
```

See the full code in [test_acr_mgr.py](https://github.com/jbcodeforce/autonomous-car-mgr/blob/main/tests/ut/test_acr_mgr.py).

### Deployment

Package the code as ZIP file (250MB limit) or container image (with 10GB limit).

Lambda can use Layer to simplify code management and reuse. The Powertools library for example can be used as a layer.

```python
powertools_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            id="lambda-powertools",
            layer_version_arn=f"arn:aws:lambda:{env.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:61"
        )

# referenced in the function definition
 acm_lambda = aws_lambda.Function(self, 'CarMgrService',
     ...
    layers=[powertools_layer],
```

But local dependencies can also being deployed as a zip (See [the product documentation- Working with .zip file archives for Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-dependencies)).

#### CDK

See an example of CDK application to deploy API Gateway, Lambda function implementing a simple microservice, and DynamoDB table [here.](https://github.com/jbcodeforce/autonomous-car-mgr/blob/main/cdk/acm/main_stack.py). 

See [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/) to get examples and API description to create anything in AWS.

As a pre-requisite developers need to bootstrap CDK in the target deployment region using `cdk bootstrap`. Then any code or IaC change can be deployed using:

```sh
cdk deploy
```

which creates a CloudFormation template.

#### [AWS SAM - Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)

AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, databases and APIs. It offers the following benefits:

* Define the application infrastructure as code quickly, using less code.
* Manage the serverless applications through their entire development lifecycle.
* Quickly provision permissions between resources with AWS SAM connectors.
* Continuously sync local changes to the cloud as we develop.
* On top of CloudFormation or Terraform.


SAM includes two parts:

1. SAM template specification: It is an extension on top of AWS CloudFormation.
1. A CLI to create new project, build and deploy, perform local debugging and testing, configure pipeline.

During deployment, SAM transforms and expands the SAM syntax into AWS CloudFormation syntax.

See [SAM templates here](https://github.com/aws/aws-sam-cli-app-templates)


See the [Getting started tutorial.](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html)

and the [creating your first API from scratch with OpenAPI and AWS SAM](https://catalog.us-east-1.prod.workshops.aws/workshops/4ff2d034-dee1-4570-93d9-11a54cc5d60c/en-US).

### Integration tests

Once the solution is deployed we can test by using the API endpoints. The tests can be defined using Python script files (under [e2e folder](https://github.com/jbcodeforce/autonomous-car-mgr/tree/main/e2e)).

```sh
python GetCarByIdUsingAPI.py 2
```

## Error Handling by execution model

As a general practice, implement error handling within each function rather than propagating errors up the call chain. This prevents failures in one function from impacting others.

Implement throttling, retries and DLQs between functions to avoid failures in one function causing cascading failures in others.

There are different ways to support error handling, depending of the integration and communication protocol.

???+ "API Gateway - synchronous call"
    * **Timeout** – API Gateway has a 30-second timeout. If the Lambda function hasn't responded to the request within 30 seconds, an error is returned to the client caller.
    * **Retries** – There are no built-in retries if a function fails to execute.
    * **Error handling** – Generate the SDK from the API stage, and use the backoff and retry mechanisms it provides.

???+ "SNS - asynch"
    * **Timeout** – Asynchronous event sources do not wait for a response from the function's execution. Requests are handed off to Lambda, where they are queued and processed by Lambda.
    * **Retries** – Asynchronous event sources have built-in retries. If a failure is returned from a function's execution, Lambda Service will attempt that invocation two more times for a total of three attempts to execute the function with its event payload. We can use the Retry Attempts configuration to set the retries to 0 or 1 instead. If Lambda is unable to invoke the function (for example, if there is not enough concurrency available and requests are getting throttled), Lambda will continue to try to run the function again for up to 6 hours by default. We can modify this duration with Maximum Event Age.
    * **Error handling** - Use the Lambda destinations OnFailure option to send failures to another destination for processing. Alternatively, move failed messages to a dead-letter queue on the function.

???+ "Kinesis Data Streams"
    * **Timeout** – When the retention period for a record expires, the record is no longer available to any consumer (24h). As an event source for Lambda, we can configure `Maximum Record Age` to tell Lambda to skip processing a data record.
    * **Retries** –  By default, Lambda retries a failing batch until the retention period for a record expires. We can configure `Maximum Retry Attempts` so that the Lambda function will skip retrying a batch of records.
    * **Error handling** - Configure an OnFailure destination on the Lambda function so that when a data record reaches the `Maximum Retry Attempts` or `Maximum Record Age`, we can send its metadata, such as shard ID and stream Amazon Resource Name (ARN), to an SQS queue or SNS topic.

???+ "SQS Queue"
    * **Timeout** – When the visibility timeout expires, messages become visible to other consumers on the queue. Set our visibility timeout to 6 times the timeout we configure for our function.
    * **Retries** – Use the `maxReceiveCount` on the queue's policy to limit the number of times Lambda will retry to process a failed execution.
    * **Error handling** - Write our functions to delete each message as it is successfully processed. Move failed messages to a dead-letter queue configured on the source SQS queue.

???+ Dead-letter queues
    We may turn on dead-letter queues and create dedicated dead-letter queue resources using Amazon SNS or Amazon SQS for individual Lambda functions that are invoked by asynchronous event source.

## Monitoring

### CloudWatch monitoring

[Lambda monitoring](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-functions-access-metrics.html) is supported by Amazon CloudWatch, with logs and metrics such as invocation count, duration, and errors. Within CloudWatch, devops can set alarms on certain metrics that may breach, to create notifications to the team.

Logs need to be added to the Function code. (print() in Python goes to the log). Use boilerplate code like AWS Powertools to control the logging level, participate in Xray reporting to view detailed traces of requests across your application and Lambda functions. This helps pinpoint where latency is occurring.

### Using AWS Powertools

[AWS Powertools](https://docs.powertools.aws.dev/lambda/python/latest/) includes methods and libraries for quickly implementing consistent logging, metrics, and traces inside your codebase.

Use X-Ray to understand end to end event flow, cross components of your solution.

### Asynchronous processing

While messages go to dead letter queues to handle errors and monitor messages sent to the DLQ. This helps track failed invocations.

## CI/CD pipeline

We recommend to follow [this workshop - Building CI/CD pipelines for Lambda canary deployments using AWS CDK](https://catalog.us-east-1.prod.workshops.aws/workshops/5195ab7c-5ded-4ee2-a1c5-775300717f42/en-US).

## Version management - Rollback

Lambda supports versioning and developer can maintain one or more versions of the lambda function. We can reduce the risk of deploying a new version by configuring the alias to send most of the traffic to the existing version, and only a small percentage of traffic to the new version. Below  is an example of creating one Alias to version 1 and a routing config with Weight at 30% to version 2. Alias enables promoting new lambda function version to production and if we need to rollback a function, we can simply update the alias to point to the desired version. Event source needs to use Alias ARN for invoking the lambda function.

    ```sh
    aws lambda create-alias --name routing-alias --function-name my-function --function-version 1  --routing-config AdditionalVersionWeights={"2"=0.03}
    ```

* Blue/green
* Version
* Traffic routing
* Rollback
