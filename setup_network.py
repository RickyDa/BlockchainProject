

import boto3
from botocore.exceptions import ClientError

# (COL_NAME, KEY_TYPE, ATTR_TYPE)
KEYS = [('node_id', 'HASH', 'S'), ('node_dns', 'RANGE', 'S')]
TABLE_NAME = 'nodes'
RW_CAPACITY = 5


def create_nodes_db():
    dynamodb = boto3.resource('dynamodb')
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': k[0],
                        'KeyType':k[1]} for k in KEYS],

            AttributeDefinitions=[{'AttributeName': k[0],
                                   'AttributeType':k[2]} for k in KEYS],

            ProvisionedThroughput={
                'ReadCapacityUnits': RW_CAPACITY,
                'WriteCapacityUnits': RW_CAPACITY})

        table.meta.client.get_waiter('table_exists').wait(TableName=TABLE_NAME)
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f'{TABLE_NAME} DB Already exists')
        return dynamodb.Table(TABLE_NAME)


def create_bucket(bucket_name, region='eu-central-1'):
    # Create bucket
    try:
        s3_client = boto3.client('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name,
                                CreateBucketConfiguration=location)
    except ClientError as e:
        print(e)
        return False
    return True


def create_ledger_sqs(name='ledger'):
    sqs = boto3.resource('sqs')

    private_sqs_params = dict(
        QueueName=f'{name}.fifo',
        Attributes={
            'FifoQueue': 'True'
        },
    )
    return sqs.create_queue(**private_sqs_params)



N = 4
# Amazon Linux 2 AMI (HVM), SSD Volume Type (My AMI)

IMAGE_ID = 'ami-07e0b9cd44928fe2f'
KEY_NAME = 'DSKey'
SECURITY_GROUP = ['launch-wizard-6']

def create_instances(num_instances):
    ec2 = boto3.resource('ec2')

    try:
        ec2.create_instances(
            ImageId=IMAGE_ID,
            MinCount=num_instances,  # [Optional] Minimum instances to launch
            MaxCount=num_instances,  # [Optional] Maximum instances to launch
            InstanceType='t2.micro',
            KeyName=KEY_NAME,
            SecurityGroups=SECURITY_GROUP
        )
        print(f'ec2 Created Successfully')
    except ClientError as e:
        print(e)
        return False
    return True


def init_blockchain():
    """
    - execute N instances with same image.
    - execute dynamodb named modes
    - s3 named blocks
    - Private SQS for each of the instances
    - SQS LEDGER named ledger
    -
    :return:
    """
    create_ledger_sqs()
    create_nodes_db()
    # create_bucket('blockchain-utils')
    create_bucket('ds-blocks')
    create_instances(num_instances=1)
    


if __name__ == '__main__':
    init_blockchain()