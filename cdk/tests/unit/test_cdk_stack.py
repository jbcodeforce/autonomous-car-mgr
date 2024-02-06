import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.acm.main_stack import ACMmainStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk/cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ACMmainStack(app, "cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

    # Add tests about lambda template created
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "app.lambda_handler",            
    })