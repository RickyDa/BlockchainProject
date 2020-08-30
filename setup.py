import boto3
from botocore.exceptions import ClientError

"""
INITIALIZE: BLOCKCHAIN NETWORK

- 2 dynamodb
- 1 SQS 
- 2 S3 BUCKET
- 5 INSTANCES
"""

PORT = 5000
TRANSACTION_LIMIT = 20
Q_NAME = 'transactions'
BUCKET_NAME_BLOCKS = 'dsblocks'
BUCKET_NAME_STATE = 'dsstates'
TRANSACTION_TABLE = 'transactions'
USER_TABLE = 'users'


NUM_INSTANCES = 5
IMAGE_ID = "ami-04cfbd64f9364a31f"
KEY = "DSKey"
SECURITY_GROUPS = ["WAID_testing"]


def create_db(table_name, keys):
    dynamodb = boto3.resource('dynamodb')
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': k[0],
                        'KeyType': k[1]} for k in keys],

            AttributeDefinitions=[{'AttributeName': k[0],
                                   'AttributeType': k[2]} for k in keys],

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


def create_instances(num_instances, image_id, key_pem, sg):
    ec2 = boto3.resource('ec2')

    try:
        ec2.create_instances(
            ImageId=image_id,
            MinCount=num_instances,  # [Optional] Minimum instances to launch
            MaxCount=num_instances,  # [Optional] Maximum instances to launch
            InstanceType='t2.micro',
            KeyName=key_pem,
            SecurityGroups=sg
        )
        print(f'ec2 Created Successfully')
    except ClientError as e:
        print(e)
        return False
    return True


if __name__ == "__main__":
    queue_name = Q_NAME

    region = 'eu-central-1'
    blocks_bucket = BUCKET_NAME_BLOCKS
    state_bucket = BUCKET_NAME_STATE
    transaction_table_name = TRANSACTION_TABLE
    transaction_keys = [('transaction_id', 'HASH', 'S')]  # (COL_NAME, KEY_TYPE, ATTR_TYPE)

    user_table_name = USER_TABLE
    user_keys = [('user_email', 'HASH', 'S')]  # (COL_NAME, KEY_TYPE, ATTR_TYPE)

    create_db(user_table_name, user_keys)
    create_db(transaction_table_name, transaction_keys)

    create_bucket(blocks_bucket, region)
    create_bucket(state_bucket, region)

    create_sqs(queue_name)

    create_instances(num_instances=NUM_INSTANCES, image_id=IMAGE_ID, key_pem=KEY, sg=SECURITY_GROUPS)
