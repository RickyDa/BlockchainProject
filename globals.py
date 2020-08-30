from utils.utils import *


class Config:
    ID = get_instance_ID()
    LEADER_ID = ''
    LEADER_DNS = ''
    PORT = 5000
    TRANSACTION_LIMIT = 20
    DNS = get_public_DNS()
    Q_NAME = 'transactions'
    BUCKET_NAME_BLOCKS = 'dsblocks'
    BUCKET_NAME_STATE = 'dsstates'
    TRANSACTION_TABLE = 'transactions'
    USER_TABLE = 'users'

    def config_to_dict(self):
        return {
            "id": self.ID,
            "dns": self.DNS,
            "leader_id": self.LEADER_ID,
            "leader_dns": self.LEADER_DNS,
            "port": self.PORT,
            "transaction_limit": self.TRANSACTION_LIMIT,
            "q_name": self.Q_NAME,
            "bucket_name": self.BUCKET_NAME_BLOCKS,
            "transaction_table": self.TRANSACTION_TABLE,
            "user_table": self.USER_TABLE
        }


cfg = Config()


class Consts:
    MUST_LOGIN_MSG = 'You must login before you create/see your transactions!'
    EMAIL_MSG = 'The email is not valid'
    TRANSACTIONS_TABLE_MSG = 'Transactions Table not exist!'
    USER_TABLE_MSG = 'Users table not exists or user logged in is not valid!'
    TRANSACTION_SIGNED_MSG = 'The transaction was signed!'
    TRANSACTION_CREATED_MSG = "Transaction created successfully"
    FAILED_LOGIN_MSG = 'Bad email or password'
    NOT_ENOUGH_AMOUNT = 'You dont have enough money!'


consts = Consts()
