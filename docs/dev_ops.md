# DevOps

Powertools has a REST resolver to annotate function to support different REST resource paths and HTTP verbs. It leads to cleaner code, and easier to test the business logic. When using Powertools REST resolver, the API Gateway API needs to be a proxy integration to Lambda as the REST resolver will use the metadata of the request.

[See the app.py code](https://github.com/jbcodeforce/autonomous-car-mgr/blob/main/src/carmgr/app.py) and how to unit test it using pytest [test_acr_mgr.py](https://github.com/jbcodeforce/autonomous-car-mgr/blob/main/tests/ut/test_acr_mgr.py).

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

* Blue/green
* Version
* Traffic routing
* Rollback
