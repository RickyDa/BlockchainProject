from utils.utils import *


class Config:
    ID = get_instance_ID()
    LEADER_ID = ''
    LEADER_DNS = ''
    PORT = 5000
    TRANSACTION_LIMIT = 20
    Q_NAME = 'transactions'
    BUCKET_NAME = 'dsblocks'
    TRANSACTION_TABLE = 'transactions'
    USER_TABLE = 'users'


cfg = Config()
