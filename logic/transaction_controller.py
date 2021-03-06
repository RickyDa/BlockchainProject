from datetime import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from globals import cfg


class Transaction:

    def __init__(self, src, dst, amount, signed=False, transaction_id=None):

        if transaction_id is None:
            self.transaction_id = str(hash(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        else:
            self.transaction_id = transaction_id

        self.src = src
        self.dst = dst
        self.amount = amount
        self.signed = signed

    def __repr__(self):
        return f'transaction_id:{self.transaction_id} ' \
               f'src:{self.src}, ' \
               f'dst:{self.dst}, ' \
               f'amount:{self.amount}, ' \
               f'signed:{self.signed}'
               
    def serialize(self):
      return dict(
            transaction_id={
                'StringValue': f'{self.transaction_id}',
                'DataType': 'String'
            },   
            src={
                'StringValue': f'{self.src}',
                'DataType': 'String'
            },
            dst={
                'StringValue': f'{self.dst}',
                'DataType': 'String'
            },
            amount={
                'StringValue': f'{self.amount}',
                'DataType': 'Number'
            }, 
            signed={
                'StringValue': f'{int(self.signed)}',
                'DataType': 'Number'
            }
        )



def send_transaction(transaction):
  try:
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=cfg.Q_NAME)
    response = queue.send_message(MessageBody = f'transaction{transaction.transaction_id}',
                                  MessageAttributes = transaction.serialize())
  except ClientError as ce:
    return None


def convert_transaction(item):
    amount = int(item['amount'])
    src = item['src']
    transaction_id = item['transaction_id']
    dst = item['dst']
    signed = item['signed']
    return Transaction(src=src, dst=dst, amount=amount, signed=signed, transaction_id=transaction_id)


def create_transaction(transaction):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(cfg.TRANSACTION_TABLE)
        return table.put_item(Item=transaction.__dict__)
    except ClientError as ce:
        return None


def get_transaction_by_key(key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(cfg.TRANSACTION_TABLE)
    response = table.query(
        KeyConditionExpression=Key('transaction_id').eq(key)
    )
    items = response['Items']
    return convert_transaction(items[0])


def get_sigh_transactions(user_email):
    # TODO get all the transactions that user_email==src or user_email==dst && transaction.signed = True
  transactions = []
  try:
      dynamodb = boto3.resource('dynamodb')
      table = dynamodb.Table(cfg.TRANSACTION_TABLE)
  
      response = table.scan(
          FilterExpression=(Attr('src').eq(user_email) | Attr('dst').eq(user_email)) & Attr('signed').eq(True)
      )
  
      for item in response['Items']:
          transactions.append(convert_transaction(item))
  
      return transactions
  except ClientError as ce:
    return transactions


def get_transactions_by_dst(dst):
    transactions = []
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(cfg.TRANSACTION_TABLE)

        response = table.scan(
            FilterExpression=Attr('dst').eq(dst) & Attr('signed').eq(False)
        )
        for item in response['Items']:
            transactions.append(convert_transaction(item))
        else:
            return transactions
    except ClientError as ce:
        return transactions


def update_transaction_by_id(transaction_id):
    transaction = get_transaction_by_key(transaction_id)
    if not transaction.signed:
        transaction.signed = True
    create_transaction(transaction)
    return transaction


def update_transaction(other):
    transaction = get_transaction_by_key(other.transaction_id)
    if transaction.signed != other.signed:
        transaction.signed = other.signed
    create_transaction(transaction)


def delete_transaction(key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(cfg.TRANSACTION_TABLE)
    table.delete_item(
        Key={'transaction_id': key}
    )
