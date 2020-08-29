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

class Consts:
  MUST_LOGIN_MSG = 'You must login before you create/see your transactions!'
  EMAIL_MSG= 'The email is not valid'
  TRANSACTIONS_TABLE_MSG = 'Transactions Table not exist!'
  USER_TABLE_MSG = 'Users table not exists or user logged in is not valid!'
  TRANSACTION_SIGNED_MSG= 'The transaction was signed!'
  TRANSACTION_CREATED_MSG = "Transaction created successfully"
  FAILED_LOGIN_MSG = 'Bad email or password'
  NOT_ENOUGH_AMOUNT = 'You dont have enough money!'
  
consts = Consts()