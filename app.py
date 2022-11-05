#!/usr/bin/env python3
import aws_cdk as cdk

from cdk.cdk_stack import CdkStack

app = cdk.App()
CdkStack(
    app,
    "pollen-rest-api",
    env=cdk.Environment(account="614871946825", region="us-east-1"),
)

app.synth()
