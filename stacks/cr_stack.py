##############################################################
#
# custom_resource_stack.py
#
# Function:
#  lambda singleton function (imported from file)
#
# Resources:
#  cfn custom resource to subscribe inspector to SNS
#
# Imports:
#  inspector_cr_role
#
##############################################################

from aws_cdk import (
  aws_cloudformation as cfn,
  aws_lambda as lambda_,
  aws_iam as iam,
  aws_ssm as ssm,
  core
)

import boto3

from uuid import uuid4

class CRStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, cr_lambda_role: iam.IRole, proj: str, **kwargs) -> None:

    super().__init__(scope, construct_id)

    # import lambda function
    with open('lambda/inspector_custom_resource.py') as fp:
      code_body=fp.read()

    # set the uuid and store it in parameter store (or read it if it already exists)
    # delete this manually when deleting the stack if desired
    ssm_client = boto3.client('ssm')

    response=ssm_client.get_parameters(Names=['cdkdemo-singleton-uuid'])

    if len(response['Parameters']) == 0:
      singleton_uuid=str(uuid4())
      #print("Creating Parameter")
      ssm_client.put_parameter(Name='cdkdemo-singleton-uuid',Value=singleton_uuid,Type='String')

    response=ssm_client.get_parameters(Names=['cdkdemo-singleton-uuid'])
    singleton_uuid=response['Parameters'][0]['Value']

    cr_lambda=lambda_.SingletonFunction(self,"Custom Lambda Singleton",
      uuid=singleton_uuid,
      code=lambda_.InlineCode(code_body),
      handler="index.lambda_handler",
      runtime=lambda_.Runtime.PYTHON_3_7,
      timeout=core.Duration.seconds(300),
      role=cr_lambda_role,
      function_name=proj+"lam-cr"
    )

    resource=core.CustomResource(self,"Custom Resource",
      service_token=cr_lambda.function_arn,
      properties=kwargs
    )

    # check for success or failure from lambda function
    self.response=resource.get_att("Response").to_string()
