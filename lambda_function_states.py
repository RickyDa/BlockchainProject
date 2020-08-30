import json
import urllib.parse
import boto3
import urllib3

"""
This file need to be copied to the lambda function 
GOTO Lab4 and paste this to the created function
"""
s3 = boto3.client('s3')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        dns_adress = key.split('.')[0]
        response = s3.get_object(Bucket=bucket, Key=key)
        http = urllib3.PoolManager()
        http.request('POST',
                     f"http://{dns_adress}:5000/updateState",
                     body=json.dumps({'snapshot': key}),
                     headers={'Content-Type': 'application/json'},
                     retries=False)
        return response['ContentType']

    except Exception as e:
        print(e)
        raise e
