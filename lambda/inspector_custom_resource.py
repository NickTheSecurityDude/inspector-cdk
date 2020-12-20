############################################################
# 
# inspector_custom_resource.py
#
# Delete Event:
#  Remove Target (sns target for inspector)
#
# Create Events:
#  Subscribe Inspector to Event (send Findings to SNS)
#
############################################################

def lambda_handler(event, context):
  import logging as log
  log.getLogger().setLevel(log.INFO)

  physical_id = 'InspectorSNSSubscriber'

  try:
    import cfnresponse
    import boto3

    inspector_client = boto3.client('inspector')
    cloudwatch_events = boto3.client('events')

    log.info('Input event: %s', event)

    if event['RequestType'] ==  'Delete':
      cloudwatch_events.remove_targets(
        Rule='inspector-assessment-template',
        Ids=['InspectorCWEventsTarget']
      )

    # Check if this is a Create and we're failing Creates
    if event['RequestType'] ==  'Create' and event['ResourceProperties'].get('FailCreate', False):
      raise RuntimeError('Create failure requested')

    # otherwise continue with the create

    # Imported Parameter Variables
    template_arn=event['ResourceProperties']['Template']
    topic_arn=event['ResourceProperties']['Topic']
    template_role_arn=event['ResourceProperties']['Template_Role']

    # subscribe to event
    inspector_client.subscribe_to_event(
      resourceArn=template_arn,
      event="FINDING_REPORTED",
      topicArn=topic_arn
    )

    # Put event topic for the cron (could go in events stack, but function not part of CDK yet)
    cloudwatch_events.put_targets(
      Rule='inspector-assessment-template',
      Targets=[{
        'Arn': template_arn,
        'Id': 'InspectorCWEventsTarget',
        'RoleArn': template_role_arn
      }]
    )

    # send success response to cloudformation stack
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Response': 'Template was subscribed to topic'}, physical_id)

  except Exception as e:
    log.exception(e)
    # cfnresponse's error message is always "see CloudWatch"
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
   
