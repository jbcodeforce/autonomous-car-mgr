# Scaling

When looking at application scaling it is important to do end to end performance testing, and review each capabilities and service limits of the services the application integrate with. Considering assessing timeouts, retry behaviors, throughput, payload size.

For example with API Gateway, there are configuration options for each API, that can help to improve access like with edge-optimized endpoint, using CloudFront distribution. Or use cache to avoid reaching backend.

Here are some good questions to address:

* Who will be using each API? 
* Where will they be accessing it from, and how frequently? 
* What are the downstream systems that could impact performance? 
* Do you need to throttle requests at the "front door" to prevent overloading a downstream component?

## SQS and Lambda

When Amazon SQS is used as a Lambda event source, the Lambda service manages polling the queue. We can set the batch size, concurrency limit, and timeout. Lambda defaults to using five parallel processes to get messages off a queue. If the Lambda service detects an increase in queue size, it will automatically increase how many batches it gets from the queue, each time. The maximum concurrency is 1000.

SQS will continue to try a failed message up to the maximum receive count specified in the re-drive policy, at which point, if a **dead-letter queue** is configured, the failed message will be put into the dead-letter queue and deleted from your SQS queue.

If the visibility timeout expires, before your Lambda function has processed the messages in that batch, any message in that batch that hasn’t been deleted by your function will become visible again. This may generate duplicate processing on the same message. The best practice, is to set your visibility timeout to six times the function timeout.

## Load testing

Perform load testing, close to the business process flow within the different component, to assess which quotas may need some tuning.

The potential tools to support load testing are:

* [Apache JMeter](https://jmeter.apache.org/)
* [Artillery Community Edition](https://www.artillery.io/)
* [Gatling](https://gatling.io/)