##########################################################################################################
#
# sns_stack.py
#
# Mappings:
#   sns principals
#
# Resources:
#   sns.Topic (SNS Inspector Topic)
#   topic.add_to_resource_policy (add resource policy for to allow inspector principal to Inspector SNS topic) 
#   topic.add_subscription (subscribe parse_inspector lambda function to SNS topic)
#   sns.Topic (Lambda Inspector SNS Topic, if needed)
#   li_topic.add_to_resource_policy (add resource policy for to allow inspector principal to Lambda Insp SNS topic)
#
# Exports:
#   inspector_topic_arn  
# 
# Imports:
#  parse_inspector_func (lambda IFunction)
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

class SNSStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, parse_inspector_func: lambda_.IFunction, env, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    self._region=env['region']
    self._account=env['account']

    sns_principals_mapping=core.CfnMapping(self,"Inspector SNS Principals",
      mapping={
        "us-west-2": {'ARN': "758058086616"},
        "us-east-1": {'ARN': "316112463485"},
        "eu-west-1": {'ARN': "357557129151"},
      }
    )

    topic=sns.Topic(self,"InspectorTopic",
      topic_name="inspector-topic"
    )

    topic.add_to_resource_policy(
      statement=iam.PolicyStatement(
        actions=["SNS:Publish"],
        principals=[iam.ArnPrincipal(
          arn=sns_principals_mapping.find_in_map(self._region,"ARN")
        )],
        resources=[topic.topic_arn]
      )
    )

    topic.add_subscription(
      subscription=sns_subs.LambdaSubscription(fn=parse_inspector_func)
    )

    self._inspector_topic_arn=topic.topic_arn

    #create Inspector Lambda SNS topic exixts
    li_topic=sns.Topic(self, "Lambda Ins SNS Topic",
      topic_name="LambdaInsSNSTopic"
    )

    li_topic.add_to_resource_policy(
      statement=iam.PolicyStatement(
        actions=["SNS:Publish"],
        principals=[iam.ArnPrincipal(
          arn=sns_principals_mapping.find_in_map(self._region,"ARN")
        )],
        resources=[topic.topic_arn]
      )
    )

    self._li_topic=li_topic

  # exports
  @property
  def inspector_topic_arn(self) -> str:
    return self._inspector_topic_arn

  @property
  def lambda_ins_topic(self) -> sns.ITopic:
    return self._li_topic
