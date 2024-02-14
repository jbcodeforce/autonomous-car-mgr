#!/usr/bin/env python3
import os

import aws_cdk as cdk

from acm.main_stack import ACMmainStack


app = cdk.App()
ACMmainStack(app, "ACSCarMgr",

    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    )

app.synth()
