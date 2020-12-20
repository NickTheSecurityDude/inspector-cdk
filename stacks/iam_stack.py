##############################################################
#
# iam_stack.py
#
# Resources:
#   Inspector Events Role
#    - 1 inline policy
#   parse_inspector Lambda Role
#    - 1 inline policy, 2 managed policies   
#   Inspector Custom Resource Role
#    - 5 inline policies, 2 managed policies
#
# Exports:
#  events_rule_iam_role_arn
#  parse_inspector_role
#  cr_lambda_role
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  core
)

class IAMStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    self._events_rule_iam_role=iam.Role(self, "Inspector Events Role", 
      role_name="AWS_Inspector_Events_Invoke_Assessment_Template",
      assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
      inline_policies=[iam.PolicyDocument(
        statements=[iam.PolicyStatement(
          actions=["inspector:StartAssessmentRun"],
          effect=iam.Effect.ALLOW,
          resources=["*"]
        )]
      )]
    )

    self._parse_inspector_role=iam.Role(self,"Parse Inspector Role",
      role_name="ParseInspectorLambdaRole",
      assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
      inline_policies=[iam.PolicyDocument(
        statements=[iam.PolicyStatement(
          actions=["sns:Publish"],
          effect=iam.Effect.ALLOW,
          resources=["*"]
        )]
      )],
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('AmazonInspectorReadOnlyAccess'),
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')  
      ]
    )

    self._cr_lambda_role=iam.Role(self,"Customer Resource Role",
      role_name="CustomResourceRole",
      assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
      inline_policies=[iam.PolicyDocument(
        statements=[
          iam.PolicyStatement(
            actions=[
              "inspector:SubscribeToEvent",
              "events:PutTargets",
              "events:RemoveTargets"
            ],
            effect=iam.Effect.ALLOW,
            resources=["*"]
          ),
          iam.PolicyStatement(
            actions=["SNS:Subscribe"],
            effect=iam.Effect.ALLOW,
            resources=[f"arn:aws:sns:{self.region}:{self.account}:LambdaInsSNSTopic"]
          ),
          iam.PolicyStatement(
            actions=["iam:PassRole"],
            effect=iam.Effect.ALLOW,
            resources=[self._events_rule_iam_role.role_arn]
          )
        ]
      )],
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaVPCAccessExecutionRole')
      ]    
    )

  # Exports
  @property
  def events_rule_iam_role_arn(self) -> str:
    return self._events_rule_iam_role.role_arn

  @property
  def parse_inspector_role(self) -> iam.IRole:
    return self._parse_inspector_role
  
  @property
  def cr_lambda_role(self) -> iam.IRole:
    return self._cr_lambda_role



