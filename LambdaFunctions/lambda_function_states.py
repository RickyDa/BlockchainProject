import json
import urllib.parse
import boto3
import urllib3

s3 = boto3.client('s3')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        address = key.split("/")[0]
        address = f"http://{address}:5000/updateState"
        body=json.dumps({'snapshot': key})
        http = urllib3.PoolManager()
        http.request('POST',
                    address,
                    body=body,
                    headers={'Content-Type': 'application/json'},
                    retries=False)
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e