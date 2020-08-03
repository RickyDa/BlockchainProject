import subprocess

BLOCKCHAIN = []
PRIVATE_SQS = ''
LEDGER_SQS = ''
BLOCKS_S3_BUCKET = ""
PUBLIC_DNS = None


# ************************* USER *************************

def save_to_a_file(fileName,itemToSave):
    try:
        f = open(fileName, "w")
        if isinstance(itemToSave, set):
            for val in itemToSave:
                print(val)
                f.write("%s\n" % val)
        f.close()
    except Exception as e:
        return "err in save_to_a_file function"


class Transaction:

    def __init__(self, amount, from_user, to_user, signed=False):
        self.amount = amount
        self.from_user = from_user
        self.to_user = to_user
        self.signed = signed

    def sign(self):
        self.signed = True


def get_public_DNS():
    """

    :return: return public DNS of this local instance
    """
    cmd = ['wget', '-qO-', 'http://instance-data/latest/meta-data/public-ipv4/']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    o, _ = proc.communicate()

    return o.decode('ascii')

def get_instance_ID():
    """
    computes instance ID(sum of ip digits) for leader election purpose

    :return: the id of the instance (sum of ip digits)
    """
    p_ip = get_public_DNS()
    return sum([int(x) for x in p_ip.split('.')])


def leader_election():
    """
        ##   Any process P can initiate an election

        ##   P sends Election messages to all process with higher IDs
            and awaits OK messages
            –   If no OK messages, P becomes coordinator and sends
                Coordinator messages to all processes with lower IDs

            –   If it receives an OK, it drops out and waits for an Coordinator
                message

        ##   If a process receives an Election

            –   Immediately sends Coordinator message if it is the process with
                highest ID

            –   Otherwise, returns an OK and starts an election

        ##  If a process receives a Coordinator message, it treats
            sender as the coordinator

    :return:
    """
    '''
        user_ip_list = get_all_users()
        ranks = find_higher_ranks()
        count_responses = 1
        while count_responses < len(ranks):
            response = send_election(get_instance_ID()) 
            count_responses+=1
    '''
    raise NotImplementedError


def get_blockchain():
    """
        Get all file names in the blocks (s3 Bucket) and sorting them.
        Then, saving the sorted list into text file(blocks.txt)
    """
    # TODO: extract all consts to another file and make the instance to read from it (not important for now)
    bucketName = 'blocksblockchain'
    fileBocketName = "blocks.txt"
    blocks_set = set()
    s3 = boto3.resource('s3')
    # s3.Bucket(bucketName).download_file(fileNameToDownload, "downloadfile.txt")
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')
    result = paginator.paginate(Bucket=bucketName)
    for page in result:
        if "Contents" in page:
            for key in page["Contents"]:
                keyString = key["Key"]
                blocks_set.add(keyString.replace(".txt", ""))
    save_to_a_file(fileBocketName, blocks_set)
    return blocks_set



def init_instance(name: str, ledger_name, blocks):
    """
        Initialize PRIVATE_SQS with the provided name
        save the instance Public DNS and the
        name of the SQS-Private on the DynamoDB and his role [LEADER,USER]
         in the network

        :param blocks: name of the s3 bucket for blocks
        :param ledger_name: name of the SQS of the signed transactions
        :param name : the SQS-private name
    """

    raise NotImplementedError


def update_blockchain(transation_name):
    """
        append to the end of the blocks.txt the transaction file name
    """
    raise NotImplementedError


def get_all_users():
    """
        From dynamoDB get all users
    """

    raise NotImplementedError


def send_transaction(amount, to_user):
    """
        Send the amount to to_user SQS queue

        :param amount: the amount that the nodes want to transact
        :param to_user: a PRIVATE_SQS name that we want to send to
    """

    raise NotImplementedError


def get_one_message_from_queue():
    """
        Get one message from PRIVATE_SQS.
    """
    raise NotImplementedError


def sign_transaction(transaction):
    """
        sign the transaction
        sign = False->true

    :param transaction:
    :return: signed transaction
    """
    transaction.signed()
    return transaction


def send_transaction_to_ledger():
    """
        send the signed transaction to the ledger
    """
    raise NotImplementedError


# *********** LEADER ***************
# TODO:
#   -add verification if the current instance is the leader
N = 4  # the amount of transactions to be saved
BLOCK_ID = 0


def get_last_block_in_the_chain():
    """
        get the the last block in the s3 bucket
        :return:
    """
    raise NotImplementedError


def get_messages_from_ledger():
    """
        Get N messages from the SQS - Ledger, and writing the into transaction_block.txt
        :return:
    """
    raise NotImplementedError


def save_new_block():
    """
        upload transaction_block.txt to BLOCKS_S3_BUCKET and delete content
        of the text file after upload.
        :return:
    """
    raise NotImplementedError


if __name__ == '__main__':
    pass
