import boto3
from botocore.exceptions import ClientError

"""
INITIALIZE: BLOCKCHAIN NETWORK

- 2 dynamodb
- 1 SQS 
- 1 S3 BUCKET
"""

def create_db(table_name,keys):
    dynamodb = boto3.resource('dynamodb')
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': k[0],
                        'KeyType':k[1]} for k in keys],

            AttributeDefinitions=[{'AttributeName': k[0],
                                   'AttributeType':k[2]} for k in keys],

            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10})

        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f'{table_name} DB Already exists')
        return dynamodb.Table(table_name)
    
    
def create_sqs(name):
    sqs = boto3.resource('sqs')
    return sqs.create_queue(QueueName=name)

     
def create_bucket(bucket_name, region=None):
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        print(e)
        return False
    return True


if __name__ == "__main__":
    queue_name = 'transactions'

    region = 'eu-central-1'
    blocks_bucket = 'dsblocks'

    transaction_table_name = 'transactions'
    transaction_keys = [('transaction_id','HASH','S')] # (COL_NAME, KEY_TYPE, ATTR_TYPE)

    user_table_name = 'users'
    user_keys = [('user_email','HASH','S')] # (COL_NAME, KEY_TYPE, ATTR_TYPE)
    
    create_db(user_table_name, user_keys)
    create_db(transaction_table_name, transaction_keys)
    create_bucket(blocks_bucket, region)
    create_sqs(queue_name)
