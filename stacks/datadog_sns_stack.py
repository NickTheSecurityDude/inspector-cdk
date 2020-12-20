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

def checkTopicExists(topic_arn):
  client=boto3.client('sns')
  #print("topic arn function")
  #print(topic_arn)
  try:
    client.get_topic_attributes(TopicArn=topic_arn)
    #print("SNS Topic Found")
    return True
  except:
    #print("SNS Topic NOT Found")
    return False

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

class SNSStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, env, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    self._region=env['region']
    self._account=env['account']


    #check if Datadog SNS topic exixts
    if checkTopicExists(f"arn:aws:sns:{self._region}:{self._account}:DatadogSNSTopic"):
      #print("SNS Topic Found - 2")
      dd_topic=sns.Topic.from_topic_arn(self,"Datadog SNS Topic",
        topic_arn=f"arn:aws:sns:{self._region}:{self._account}:DatadogSNSTopic"
      )
    else:
      #print("SNS Topic NOT Found - 2")
      dd_topic=sns.Topic(self, "Datadog SNS Topic",
        topic_name="DatadogSNSTopic"
      )
    
    dd_topic.add_to_resource_policy(
      statement=iam.PolicyStatement(
        actions=["SNS:Publish"],
        principals=[iam.ArnPrincipal(
          arn=sns_principals_mapping.find_in_map(self._region,"ARN")
        )],
        resources=[topic.topic_arn]
      )
    )

    datadog_fwd_name=getDatadogLambdaFunction(
        f"arn:aws:lambda:{env['region']}:{env['account']}:function:datadog-forwarder-Forwarder-"
      )

    datadog_fwd_lambda=lambda_.Function.from_function_arn(self,"Datadog SNS Function",datadog_fwd_name)

    dd_topic.add_subscription(
      subscription=sns_subs.LambdaSubscription(
        fn=datadog_fwd_lambda
      )
    )

    #add permission for sns to push to datadog lambda function
    lambda_.CfnPermission(self,"dd-fwd-lamd-perm",
      action="lambda:InvokeFunction",
      function_name=datadog_fwd_name,
      principal="sns.amazonaws.com",
      source_arn=f"arn:aws:sns:{env['region']}:{env['account']}:DatadogSNSTopic"
    )

