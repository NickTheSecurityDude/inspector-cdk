########################################################################################
#
# events_stack.py
#
# Resources:
#   events.Rule (cron for inspector)
#   put_targets (target for cron)  XX - Does not exist in cdk yet use cr lambda
#
# Imports:  XX - Does not exist in cdk yet use cr lambda
#   template_arn (from Inspector stack)
#   template_arn_role (from IAM stack)
#
########################################################################################

from aws_cdk import (
  aws_events as events,
  aws_iam as iam,
  #aws_events_targets as targets,
  core
)

class EventsStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str,  **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # add cloudwatch cron
    events_rule=events.Rule(self,"InspectorCronRule",
      description="Inspector Template Events Cron Rule",
      rule_name="inspector-template-assessment",
      schedule=events.Schedule.cron(minute="0",hour="15")
    )

    # add target to cron
    # XX - Does not exist in cdk yet use cr lambda


