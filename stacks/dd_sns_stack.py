##########################################################################################################
#
# sns_stack.py
#
# Functions:
#   checkTopicExists (check for DataDog SNS topic)
#   getDatadogLambdaFunction (DataDog Lambda forwarder function)
#
# Resources:
#   sns.Topic (Datadog SNS Topic, if needed)
#   dd_topic.add_to_resource_policy (add resource policy for to allow inspector principal to Datadog SNS topic)
#   dd_topic.add_subscription (add Datadog fowarder lambda function as subscriber to Datadog SNS topic)
#
#
#########################################################################################################

from aws_cdk import (
  aws_sns as sns,
  aws_sns_subscriptions as sns_subs,
  aws_iam as iam,
  aws_lambda as lambda_,
  aws_events as events,
  core
)

import boto3

def getDatadogLambdaFunction(arn_prefix):
  client=boto3.client('lambda')
  #print("prefix ************")
  #print(arn_prefix)
  response=client.list_functions(
    FunctionVersion='ALL'
  )
  found_sw=0
  for f in response.get('Functions', []):
    #print(f.get('FunctionArn', ''))
    if arn_prefix in f.get('FunctionArn', ''):
      #print('prefix found')
      # trim suffix :$LATEST
      func_arn=f.get('FunctionArn').replace(':$LATEST','')
      found_sw=1
      return func_arn

  if found_sw==0:  
    return False

class DDSNSStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, li_topic: sns.ITopic, env, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    self._region=env['region']
    self._account=env['account']


    #Inspector Lambda SNS topic
    

    datadog_fwd_name=getDatadogLambdaFunction(
        f"arn:aws:lambda:{env['region']}:{env['account']}:function:datadog-forwarder-Forwarder-"
      )

    datadog_fwd_lambda=lambda_.Function.from_function_arn(self,"Datadog SNS Function",datadog_fwd_name)

    li_topic.add_subscription(
      subscription=sns_subs.LambdaSubscription(
        fn=datadog_fwd_lambda
      )
    )

    #add permission for sns to push to datadog lambda function
    lambda_.CfnPermission(self,"dd-fwd-lamd-perm",
      action="lambda:InvokeFunction",
      function_name=datadog_fwd_name,
      principal="sns.amazonaws.com",
      source_arn=f"arn:aws:sns:{env['region']}:{env['account']}:LambdaInsSNSTopic"
    )

