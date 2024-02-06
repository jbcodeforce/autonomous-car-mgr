from aws_cdk import (
    # Duration,
    RemovalPolicy,
    Stack,
    aws_lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
     aws_cloudwatch,
     CfnOutput,
    aws_iam,
)
from datetime import datetime
from constructs import Construct

class ACMmainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        current_date =  datetime.now().strftime('%d-%m-%Y')   
        managed_policy_insights = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            'CloudWatchLambdaInsightsExecutionRolePolicy')
        
        managed_policy_basic_exec = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            'service-role/AWSLambdaBasicExecutionRole')
        
        lambda_role = aws_iam.Role(self,
                               id='acm-lambda-role',
                               assumed_by=aws_iam.ServicePrincipal(
                                   'lambda.amazonaws.com'),
                               managed_policies=[managed_policy_insights, managed_policy_basic_exec])
        
        table = dynamodb.TableV2(self, "CarsTable",
                table_name="acm_cars",
                partition_key=dynamodb.Attribute(name="car_id", type=dynamodb.AttributeType.STRING),
                table_class=dynamodb.TableClass.STANDARD_INFREQUENT_ACCESS,
                billing=dynamodb.Billing.on_demand(),
                removal_policy=RemovalPolicy.DESTROY,
                )
       
        acm_lambda = aws_lambda.Function(self, 'CarMgrHandler',
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code= aws_lambda.Code.from_asset('../src/carmgr'),
            function_name= "CarManagerHandler",
            handler='app.handler',
            role=lambda_role,
            environment = {
                "CAR_TABLE_NAME":table.table_name
            },
            current_version_options = aws_lambda.VersionOptions(
                description = f'Version deployed on {current_date}',
                removal_policy = RemovalPolicy.RETAIN
            )
        )

        new_version = acm_lambda.current_version
        new_version.apply_removal_policy(RemovalPolicy.RETAIN)

        alias = aws_lambda.Alias(
            scope = self,
            id = "FunctionAlias",
            alias_name = acm_lambda.function_name,
            version = new_version
        )

        table.grant_read_write_data(acm_lambda)

        base_api = apigw.LambdaRestApi(
            self, 'AcrEndpoint',
            rest_api_name='api-car-mgr',
            handler=alias,
            proxy=False,
            deploy_options = apigw.StageOptions(stage_name="prod")
        )

        cars_resource=base_api.root.add_resource('cars')
        cars_resource.add_method("GET",apigw.LambdaIntegration(alias))
        
        CfnOutput(
            self, 
            "LAMBDA FUNCTION NAME", 
            value=acm_lambda.function_name
        )

        CfnOutput(
            self, 
            "DYNAMODB TABLE NAME", 
            value=table.table_name
        )

        CfnOutput(
            self, 
            "APIGTW URL", 
            value=base_api.url
        )


        
       
        


