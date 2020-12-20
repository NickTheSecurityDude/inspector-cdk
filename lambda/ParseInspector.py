import json
import boto3
import datetime
from dateutil.tz import tzlocal

def lambda_handler(event, context):
  acct_id=context.invoked_function_arn.split(":")[4]
  region=context.invoked_function_arn.split(":")[3]

  test_mode=0
  print("Test Mode: "+str(test_mode))
  email_sns_arn="arn:aws:sns:"+region+":"+acct_id+":LambdaInsSNSTopic"

  client = boto3.client('inspector')
  print(event)

  print("Message")
  print(event['Records'][0]['Sns']['Message'])
  finding_arns=json.loads(event['Records'][0]['Sns']['Message'])['finding']
  print("Finding ARN:")
  print(finding_arns)
  
  arn = email_sns_arn     
  response = client.describe_findings(
    findingArns=[finding_arns])
  print(response['findings'])
  string1=""
  for finding in response['findings']:
    #string1+=finding['title']+"\n"
    #message="Run: "+run+"\nLAMBDA high vulnerability: "+string1
    message=finding
    print(finding)
    print(finding['title'])

  print(message)
  
  #convert date functions to string
  message['updatedAt']=str(message['updatedAt'])
  message['createdAt']=str(message['createdAt'])
  
  client = boto3.client('sns')
  response = client.publish(
    TargetArn=arn,
    Message=json.dumps(message),
  )
  return 1
