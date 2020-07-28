import subprocess

BLOCKCHAIN = []
PRIVATE_SQS = ''
LEDGER_SQS = ''
BLOCKS_S3_BUCKET = ""
PUBLIC_DNS = None


# ************************* USER *************************
class Transaction:

    def __init__(self, amount, from_user, to_user, signed=False):
        self.amount = amount
        self.from_user = from_user
        self.to_user = to_user
        self.signed = signed

    def sign(self):
        self.signed = True


def leader_election():
    raise NotImplementedError


def get_public_DNS():
    """

    :return: return public DNS of this local instance
    """
    cmd = ['wget', '-qO-', 'http://instance-data/latest/meta-data/public-ipv4/']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    o, _ = proc.communicate()

    return o.decode('ascii')


def instance_ID():
    """
    computes instance ID(sum of ip digits) for leader election purpose

    :return: the id of the instance (sum of ip digits)
    """
    p_ip = get_public_DNS()
    return sum([int(x) for x in p_ip.split('.')])


def get_blockchain():
    """
        Get all file names in the blocks (s3 Bucket) and sorting them.
        and saving the sorted list into text file(blocks.txt)

    """

    raise NotImplementedError


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
