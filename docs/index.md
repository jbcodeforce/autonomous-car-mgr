# Autonomous Car Manager Service

A simple application to manage an inventory of Autonomous Robot Cars. This is to demonstrate some of the microservice implementation in Lambda with functional and stress testing.

## Questions this repository try to answer

### Architecture Patterns

* [x] Review Lambda runtime architecture
* [x] Serverless architecture patterns: how to map to a microservice approach ? what are the best practices for using Lambda functions to ensure loose coupling and service autonomy?
* How to use event sourcing with Lambda? 
* How to handle state management in a stateless environment like AWS Lambda, especially for complex workflows or transactions?
* What are the best practices for integrating AWS Lambda with other AWS services, particularly for event-driven architectures?
* How to design Lambda functions to handle events from multiple sources, and what considerations are there for managing event source mappings?
* How do AWS Lambda's service limits impact architectural decisions, and what strategies can be used to mitigate potential limitations?
* Are there specific scenarios where AWS Lambda might not be the best choice, and what alternatives to consider?
* How to integrate API Gateway with Lambda functions to scale demand? 
* How to use AWS Step Functions to orchestrate multiple Lambda functions for complex workflows?
* What are the best practices for using event source mappings with Lambda to process records from streams or queues?

[>>> See discussions in architecture section](./architecture.md)

### Scaling

* How to scale lambda for high-traffic applications and how to monitor scaling?
* How to optimize Lambda function for performance?
* Review strategy to minimize cold start?
* Optimizing for high-throughput?
* How does the allocated memory size affect the execution time and cost of Lambda functions?
* How to balance performance / cost?

[>>> See discussions in scaling section](./scaling.md)

### Security

* What are the best practices to secure Lambda functions, especially in terms of managing permissions and access controls?
* How should sensitive data be managed within Lambda environments?
* How to manage secrets?
* How to manage IAM roles and permissions for Lambda functions to ensure principle of least privilege?
* How to support encrypting sensitive data processed by Lambda functions, both in transit and at rest?

[>>> See discussions in security section](./security.md)

### Cost Optimization

* How to optimize AWS Lambda costs for a large-scale application, and what tools or metrics are most useful for monitoring and controlling Lambda expenses?
* Are there specific patterns or architectural choices that significantly affect cost, and what are the considerations to balance cost with performance?
* How does AWS Lambda's pricing model scale beyond the free tier, and what measures can be taken to predict and control expenditure?

[>>> See discussions in cost section](./cost.md)

### Development, Operation and CI/CD

* What are the best practices for deploying Lambda functions in a CI/CD pipeline, and how to manage version control and rollbacks?
* How to support blue-green deployments or canary releases with AWS Lambda?
* How should error handling be implemented in AWS Lambda to ensure reliability and fault tolerance?
* What to monitor and logging tools or practices do you recommend for AWS Lambda functions to ensure proactive issue resolution?
* What tools to do local development and testing of AWS Lambda functions?
* How can teams effectively debug Lambda functions, particularly when integrated with other AWS services?
* How to adopt CI/CD practices for Lambda functions? How to automate deployment while ensuring rollback capabilities for stability?
* How to effectively use versioning and aliases in AWS Lambda to manage deployments and facilitate A/B testing?
* Beyond CloudWatch, are there any third-party tools or AWS services that provide deeper insights into Lambda function performance and health?
* How to implement anomaly detection in Lambda executions to quickly identify and respond to unusual patterns or errors?

[>>> See discussions in development and operations section](./dev_ops.md)

## A benchmark application

To support the discussions addressed in this repository, I will use a simple application using API Gateway, Lambda, DynamoDB and adds feature on top of it.

The application starts with the simplest deployment as illustrated in the following diagrams:

![](./diagrams/acm-base.drawio.png)