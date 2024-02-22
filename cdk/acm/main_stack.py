from aws_cdk import (
    # Duration,
    BundlingOptions,
    Environment,
    RemovalPolicy,
    Stack,
    aws_lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
     aws_cloudwatch,
     aws_events,
     aws_sns,
     aws_events_targets,
     CfnOutput,
     aws_logs,
    aws_iam,
    aws_secretsmanager,
    aws_codedeploy
)
from datetime import datetime
import json
from constructs import Construct


DEFAULT_SECRET_NAME="ACS_secret"

'''
Define DynamoDB table to persist autonomous cars as part of the robot taxi inventory.
Define the Lambda Function to support the management operation on the AutonomousCar entity
Define the API Gateway to expose the Lambda Function as a REST API.
The Autonomous car manager is event-driven so produce AutonomousCar entity status update events 
'''
class ACMmainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,env: Environment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        carTable=self.defineCarTableDataBase()
        carEventBus = aws_events.EventBus(self, "carsEventBus",
                    event_bus_name="cars"
                )
        acm_lambda, alias= self.defineAutonomousCarManagerAsLambdaFct(carTable,carEventBus,env)
        self.defineAutonomousCarManagerAPIs(alias)
        self.code_deploy_app(alias)
        carEventBus.grant_all_put_events(acm_lambda)
        self.defineSNSTargetToEventBus(carEventBus)
        self.defineCWlogsAsTargetToEventBus(carEventBus)
        secrets=self.secret_in_aws_secrets()
        secrets.grant_read(grantee=acm_lambda)
    # end of constructor ------------------    


    def defineUserRoleForLambdaExecution(self):
        managed_policy_insights = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            'CloudWatchLambdaInsightsExecutionRolePolicy')
        
        managed_policy_basic_exec = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            'service-role/AWSLambdaBasicExecutionRole')
        
        return aws_iam.Role(self,
                               id='acm-lambda-role',
                               assumed_by=aws_iam.ServicePrincipal(
                                   'lambda.amazonaws.com'),
                               managed_policies=[managed_policy_insights, managed_policy_basic_exec])
        


    def defineCarTableDataBase(self):
        carTable = dynamodb.TableV2(self, "CarsTable",
                table_name="acm_cars",
                partition_key=dynamodb.Attribute(name="car_id", type=dynamodb.AttributeType.STRING),
                table_class=dynamodb.TableClass.STANDARD_INFREQUENT_ACCESS,
                billing=dynamodb.Billing.on_demand(),
                removal_policy=RemovalPolicy.DESTROY,
                )
        CfnOutput(
            self, 
            "DYNAMODB TABLE NAME", 
            value=carTable.table_name
        )
        return carTable



    def defineAutonomousCarManagerAsLambdaFct(self, carTable,carEventBus,env):
        lambda_role = self.defineUserRoleForLambdaExecution()
        powertools_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            id="lambda-powertools",
            layer_version_arn=f"arn:aws:lambda:{env.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:61"
        )
        current_date =  datetime.now().strftime('%d-%m-%Y')   
        acm_lambda = aws_lambda.Function(self, 'CarMgrService',
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code= aws_lambda.Code.from_asset(path="../src/",
                                             bundling=BundlingOptions(
                                                 image= aws_lambda.Runtime.PYTHON_3_11.bundling_image,
                                                 command= [
                                                     'bash','-c','pip3 install -r requirements.txt  --python-version 3.11 --only-binary=:all: -t /asset-output && cp -rau . /asset-output'
                                                 ],
                                            )),
            function_name= "CarMgrService",
            handler='app.handler',
            role=lambda_role,
            layers=[powertools_layer],
            environment = {
                "CAR_EVENT_BUS":carEventBus.event_bus_name,
                "CAR_TABLE_NAME":carTable.table_name,
                "secret_name": DEFAULT_SECRET_NAME,
                "POWERTOOLS_SERVICE_NAME": "CarManager",
                "POWERTOOLS_METRICS_NAMESPACE": "CarManager",
                "POWERTOOLS_LOG_LEVEL": "INFO",
            },
            current_version_options = aws_lambda.VersionOptions(
                description = f'Version deployed on {current_date}',
                removal_policy = RemovalPolicy.RETAIN
            )
        )

        carTable.grant_read_write_data(acm_lambda)

        new_version = acm_lambda.current_version
        new_version.apply_removal_policy(RemovalPolicy.RETAIN)

        alias = aws_lambda.Alias(
            scope = self,
            id = "FunctionAlias",
            alias_name = acm_lambda.function_name,
            version = new_version
        )

        CfnOutput(
            self, 
            "LAMBDA FUNCTION NAME", 
            value=acm_lambda.function_name
        )
        return acm_lambda,alias


    def defineAutonomousCarManagerAPIs(self, alias):
        base_api = apigw.LambdaRestApi(
            self, 'AcrEndpoint',
            rest_api_name='acs_car_ng_svc',
            handler=alias,
            cloud_watch_role=True,
            proxy=False,
            deploy_options = apigw.StageOptions(stage_name="dev")
        )

        cars_resource=base_api.root.add_resource('cars')
        cars_resource.add_method("GET") # get all cars
        cars_resource.add_method("POST")
        cars_resource.add_method("PUT")
        car = cars_resource.add_resource("{car_id}")
        car.add_method("GET")
        CfnOutput(
            self, 
            "APIGTW URL", 
            value=base_api.url
        )
        return base_api
    
    def defineSNSTargetToEventBus(self, carEventBus):
        snsTopic = aws_sns.Topic(self, "acm-sns-topic",
                    topic_name="acm-cars-topic",
                    display_name="Autonomous Car Manager SNS topic"
                )
        routingRuleToSNS = aws_events.Rule(self, "routingRuleToSNS",
                    event_bus=carEventBus,
                    event_pattern=aws_events.EventPattern(
                        source=["acs.acm"],
                        detail_type=["acme.acs.acm.events.CarUpdated"]
                    ),
                    targets=[aws_events_targets.SnsTopic(snsTopic)]
                )
        CfnOutput(self, "SNS Topic ARN", value=snsTopic.topic_arn)
        CfnOutput(self, "SNS Topic NAME", value=snsTopic.topic_name)

    def defineCWlogsAsTargetToEventBus(self, carEventBus):
        cwLogsGroup = aws_logs.LogGroup(self, "acm-eb-logs-group",
                    log_group_name="acm-eb-cars-logs",
                    removal_policy=RemovalPolicy.DESTROY
                )
        routingRuleToCWLogs = aws_events.Rule(self, "routingRuleToCWLogs",
                    event_bus=carEventBus,
                    event_pattern=aws_events.EventPattern(
                        source=["acs.acm"],
                        detail_type=["acme.acs.acm.events.CarUpdated"]
                    ),
                    targets=[aws_events_targets.CloudWatchLogGroup(cwLogsGroup)]
                )
        CfnOutput(self, "CW Logs Group", value=cwLogsGroup.log_group_name)
        CfnOutput(self, "CW Logs Group ARN", value=cwLogsGroup.log_group_arn)
        CfnOutput(self, "CW Logs Group Name", value=cwLogsGroup.log_group_name)

    """
    Create a new secret in AWS SecretManager
    Secret DEFAULT_SECRET_NAME will have multiple object values as defined by secret_string_template
    and with specific encrypted value of the generate_string_key
    """
    def secret_in_aws_secrets(self):
        return aws_secretsmanager.Secret(self,
                                  "ACMsecrets",
                                secret_name=DEFAULT_SECRET_NAME,
                                generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                                    secret_string_template=json.dumps({"username": "postgres"}),
                                    generate_string_key="password",
                                    exclude_characters="/@"
                                ))
    
    def code_deploy_app(self,fctAlias):
        application=  aws_codedeploy.LambdaApplication(self, "AcmCodeDeploy",
            application_name="AcmMicroservice"
        )
        deployment_group = aws_codedeploy.LambdaDeploymentGroup(self, "AcmBlueGreenDeployment",
            application=application,  # optional property: one will be created for you if not provided
            alias=fctAlias,
            deployment_config=aws_codedeploy.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE
        )
        return application