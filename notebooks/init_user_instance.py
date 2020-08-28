
import boto3
import botocore
import subprocess

PUBLIC_DNS = ''
ID = ''
TRANSACTION_SQS = None
TRANSACTION_SQS_NAME = ''


def get_public_DNS():
    global PUBLIC_DNS
    """

    :return: return public DNS of this local instance
    """
    cmd = ['wget', '-qO-', 'http://instance-data/latest/meta-data/public-ipv4/']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    o, _ = proc.communicate()
    PUBLIC_DNS = o.decode('ascii')
    return PUBLIC_DNS


def get_instance_ID():
    global ID
    """
    computes instance ID(sum of ip digits) for leader election purpose

    :return: the id of the instance (sum of ip digits)
    """
    # TODO ID is not atomic
    p_ip = get_public_DNS()
    ID = str(sum([int(x) for x in p_ip.split('.')]))
    return ID


def create_transaction_sqs():
    global TRANSACTION_SQS, TRANSACTION_SQS_NAME
    """

     Create the private sqs

    """
    TRANSACTION_SQS_NAME = f'{ID}.fifo'
    private_sqs_params = dict(
        QueueName=TRANSACTION_SQS_NAME,
        Attributes={
            'FifoQueue': 'True'
        },
    )
    # Get the service resource
    sqs = boto3.resource('sqs')
    TRANSACTION_SQS = sqs.create_queue(**private_sqs_params)


def register(table_name='nodes'):
    """
        save the instance Public DNS and the
        name of the SQS-Private on the DynamoDB and his role [LEADER,USER]
        in the network
    """

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'node_id': ID,
                'node_dns': PUBLIC_DNS,
                'message_q': TRANSACTION_SQS_NAME,
                # TODO: How to decide a nodes role
                'role': 'user',
            }
        )
    except Exception as e:
        print(e)
        print('USER NOT REGISTERED.')

    print(f'private sqs at:{TRANSACTION_SQS.url}')
    print('Node initialized')


def init_instance():
    get_public_DNS()
    get_instance_ID()
    create_transaction_sqs()
    register()
    return PUBLIC_DNS, ID, TRANSACTION_SQS, TRANSACTION_SQS_NAME


if __name__ == '__main__':
    get_public_DNS()
    get_instance_ID()
    create_transaction_sqs()
    register()
