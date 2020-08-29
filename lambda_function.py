import json
import urllib.parse
import boto3
import urllib3

"""
This file need to be copied to the lambda function 
GOTO Lab4 and paste this to the created function
"""
s3 = boto3.client('s3')


def get_instances():
    instances = []
    ec2 = boto3.client('ec2',
                       region_name="eu-central-1",
                       aws_access_key_id="<YOUR aws_access_key_id>",
                       aws_secret_access_key="<YOUR aws_secret_access_key>")
    response = ec2.describe_instances()

    for res in response['Reservations']:
        for inst in res['Instances']:
            if 'PublicIpAddress' in inst.keys():
                instances.append(inst['PublicIpAddress'])

    return instances


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        instances = get_instances()
        http = urllib3.PoolManager()
        for inst in instances:
            http.request('POST',
                         f"http://{inst}:5000/updateblocks",
                         body=json.dumps({'block': key.split('.')[0]}),
                         headers={'Content-Type': 'application/json'},
                         retries=False)
        return response['ContentType']

    except Exception as e:
        print(e)
        raise e
