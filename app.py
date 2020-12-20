#!/usr/bin/env python3

##################################################################
#
# app.py - STACKS
# 
# 1. IAM
# 2. Inspector
# 3. Events
# 4. Lambda
# 5. SNSStack
# 6. Custom Resource
#
# Notes:
#  bootstrap to create s3 bucket and upload lambda function
#  cdk bootstrap aws://<account-id>/<region>
#
###################################################################

from aws_cdk import core

# Datadog forwarder flag
ENABLE_DD=1

if ENABLE_DD==1:
  from stacks.dd_sns_stack import getDatadogLambdaFunction

import boto3
client = boto3.client('sts')
region=client.meta.region_name
account_id = client.get_caller_identity()["Account"]

my_env = {'region': region, 'account': account_id}

# check for Datadog forwarder
# https://docs.datadoghq.com/serverless/forwarder/

if ENABLE_DD==1:
  arn_prefix=f"arn:aws:lambda:{my_env['region']}:{my_env['account']}:function:datadog-forwarder-Forwarder-"

  if not getDatadogLambdaFunction(arn_prefix):
    print(f"ERROR: Datadog Forwarder Not Found in Region: {my_env['region']}")
    print("Run the Datadog Forwarder Template Located Here:")
    print("https://docs.datadoghq.com/serverless/forwarder/")
    raise Exception("Required Lambda Function Not Found, see previous messages")


proj="cdkdemo-"

from stacks.iam_stack import IAMStack
from stacks.inspector_stack import InspectorStack
from stacks.events_stack import EventsStack
from stacks.lambda_stack import LambdaStack
from stacks.sns_stack import SNSStack
from stacks.cr_stack import CRStack

if ENABLE_DD==1:
  from stacks.dd_sns_stack import DDSNSStack

app = core.App()

iam_stack=IAMStack(app, proj+"iam")
inspector_stack=InspectorStack(app, proj+"inspector")
events_stack=EventsStack(app, proj+"events")
lambda_stack=LambdaStack(app,proj+"lambda",parse_inspector_role=iam_stack.parse_inspector_role)
sns_stack=SNSStack(app,proj+"sns",parse_inspector_func=lambda_stack.parse_inspector_func,env=my_env)
cr_stack=CRStack(app,proj+"cust-res",
  cr_lambda_role=iam_stack.cr_lambda_role,
  Template=inspector_stack.assessment_template_arn,
  Topic=sns_stack.inspector_topic_arn,
  Template_Role=iam_stack.events_rule_iam_role_arn,
  proj=proj
)

if ENABLE_DD==1:
  dd_sns_stack=DDSNSStack(app,proj+"dd-sns",sns_stack.lambda_ins_topic,env=my_env)

app.synth()
