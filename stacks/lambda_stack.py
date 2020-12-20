##############################################################
#
# lambda_stack.py
#
# Resources:
#  lambda function (code in /lambda folder (from_asset))
#
# Exports:
#  parse_inspector_func
#
# Imports:
#  parse_inspector_role
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  aws_lambda as lambda_,
  core
)

class LambdaStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, parse_inspector_role: iam.IRole, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)


    self._parse_inspector_func=lambda_.Function(self,"Parse Inspector Lambda Func",
      code=lambda_.Code.from_asset("lambda"),
      handler="ParseInspector.lambda_handler",
      runtime=lambda_.Runtime.PYTHON_3_8,
      role=parse_inspector_role
    )

  # Exports
  @property
  def parse_inspector_func(self) -> lambda_.IFunction:
    return self._parse_inspector_func
