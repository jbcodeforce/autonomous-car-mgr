# [Autonomous Car Manager Service](https://jbcodeforce.github.io/autonomous-car-mgr/)


A simple application to manage an inventory of Autonomous Robot Cars. This is to demonstrate some of the microservice implementation with Amazon Lambda with functional and stress testing.

[Read documentation in book format](https://jbcodeforce.github.io/autonomous-car-mgr/) for detail on Lambda implementation and deployment best practices.

## Requirements

The application supports CRU operations on an Autonomous Car. This is a simple microservice about managing the life cycle of an autonomous car as part of Acme Inc car inventory. The cars are used as robot taxis.

![](./docs/diagrams/acm-base.drawio.png)

## Iterative development

* From the root folder of this repository, setup a local python environment:

```sh
 python3 -m venv .devenv
 source .devenv/bin/activate
```

The source code for the Lambda functions is under src.

* Unit tests the Lambda function

```sh
# under tests/ut
pytest
```

* Deploy using CDK

```sh
#under cdk folder
cdk synth 
cdk deploy
```

## Implementation

The implementation for the Lambda use Python and [AWS Powertools](https://docs.powertools.aws.dev/lambda/python/latest/) to get the boiler plate for monitoring and tracing. 

Infrastructure as Code is done using Python CDK.

![](https://jbcodeforce.github.io/yarfba/serverless/diagrams/event-b-solution.drawio.png)


