#################################################################################################
#
# inspector_stack.py
#
# Mapping:
#  Inspector Rule Packages Mappings
#
# Resources (Level 1 - Low Level Constructs):
#  CfnResourceGroup (use tags to determine which instances to scan)
#  CfnAssessmentTarget (add tagged instances to target)
#  CfnAssessmentTemplate (which packages to use when scanning, remove CIS if not needed)
#
# Exports:
#  assessment_template_arn
#
################################################################################################

from aws_cdk import (
  aws_events as events,
  aws_inspector as inspector,
  core
)

class InspectorStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    inspector_rules_mapping = core.CfnMapping(
      scope = self,
      id = "Inspector Rule packages",
      mapping = {
        "eu-central-1": {
          "CVE": "arn:aws:inspector:eu-central-1:537503971621:rulespackage/0-wNqHa8M9",
          "CIS": "arn:aws:inspector:eu-central-1:537503971621:rulespackage/0-nZrAVuv8",
          "securityBestPractices": "arn:aws:inspector:eu-central-1:537503971621:rulespackage/0-ZujVHEPB",
          "runtimeBehaviorAnalysis": "arn:aws:inspector:eu-central-1:537503971621:rulespackage/0-0GMUM6fg"
        },
        "eu-west-1": {
          "CVE": "arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-ubA5XvBh",
          "CIS": "arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-sJBhCr0F",
          "securityBestPractices": "arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-SnojL3Z6",
          "runtimeBehaviorAnalysis": "arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-lLmwe1zd"
        },
        "us-east-1": {
          "CVE": "arn:aws:inspector:us-east-1:316112463485:rulespackage/0-gEjTy7T7",
          "CIS": "arn:aws:inspector:us-east-1:316112463485:rulespackage/0-rExsr2X8",
          "securityBestPractices": "arn:aws:inspector:us-east-1:316112463485:rulespackage/0-R01qwB5Q",
          "runtimeBehaviorAnalysis": "arn:aws:inspector:us-east-1:316112463485:rulespackage/0-gBONHN9h"
        },
        "us-east-2": {
          "CVE": "arn:aws:inspector:us-east-2:646659390643:rulespackage/0-JnA8Zp85",
          "CIS": "arn:aws:inspector:us-east-2:646659390643:rulespackage/0-m8r61nnh",
          "securityBestPractices": "arn:aws:inspector:us-east-2:646659390643:rulespackage/0-AxKmMHPX",
          "runtimeBehaviorAnalysis": "arn:aws:inspector:us-east-2:646659390643:rulespackage/0-UCYZFKPV"
        },
        "us-west-2": {
          "CVE": "arn:aws:inspector:us-west-2:758058086616:rulespackage/0-9hgA516p",
          "CIS": "arn:aws:inspector:us-west-2:758058086616:rulespackage/0-H5hpSawc",
          "securityBestPractices": "arn:aws:inspector:us-west-2:758058086616:rulespackage/0-rD1z6dpl",
          "runtimeBehaviorAnalysis": "arn:aws:inspector:us-west-2:758058086616:rulespackage/0-JJOtZiqQ"
        },
      }
    )

    resource_group=inspector.CfnResourceGroup(self,"Inspector Resource Group",
      resource_group_tags=[core.CfnTag(key="inspector",value="True")]
    )

    assessment_target=inspector.CfnAssessmentTarget(self,"Inspector Target",
      resource_group_arn=resource_group.attr_arn
    )

    assessment_template=inspector.CfnAssessmentTemplate(self,"Inspector Template",
      assessment_target_arn=assessment_target.attr_arn,
      # increase this value after testing to something like 900 or 3600
      duration_in_seconds=300,
      rules_package_arns=[
        inspector_rules_mapping.find_in_map(self.region,package) for package in (
          "CVE",
          "CIS",
          "securityBestPractices",
          "runtimeBehaviorAnalysis"
        )
      ]
    )

    # use a local variable for good measure
    self._assessment_template_arn=assessment_template.attr_arn

  #exports   
  @property   
  def assessment_template_arn(self) -> str:
    return self._assessment_template_arn

