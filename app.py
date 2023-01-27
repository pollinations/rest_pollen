#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack

dev_or_prod = os.environ.get("DEV_OR_PROD", "dev")

if dev_or_prod == "dev":
    stack_name = "pollen-rest-api-dev"
elif dev_or_prod == "prod":
    stack_name = "pollen-rest-api"
elif dev_or_prod == "prod2":
    stack_name = "pollen-rest-api-prod"

app = cdk.App()
CdkStack(
    app,
    stack_name,
    env=cdk.Environment(account="614871946825", region="us-east-1"),
)

app.synth()
