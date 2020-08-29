from datetime import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


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


def convert_transaction(item):
    amount = int(item['amount'])
    src = item['src']
    transaction_id = item['transaction_id']
    dst = item['dst']
    signed = item['signed']
    return Transaction(src=src, dst=dst, amount=amount, signed=signed, transaction_id=transaction_id)


def create_transaction(transaction, table_name='transactions'):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        return table.put_item(Item=transaction.__dict__)
    except ClientError as ce:
        return None


def get_transaction_by_key(key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('transactions')
    response = table.query(
        KeyConditionExpression=Key('transaction_id').eq(key)
    )
    items = response['Items']
    return convert_transaction(items[0])


def get_sigh_transactions(user_email):
    # TODO get all the transactions that user_email==src or user_email==dst && transaction.signed = True
    # mock_data = [Transaction("dorel@gamil.com", "ricky@gamil.com", 20, True)]
    transactions = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('transactions')

    response = table.scan(
        FilterExpression=(Attr('src').eq(user_email) | Attr('dst').eq(user_email)) & Attr('signed').eq(True)
    )

    for item in response['Items']:
        transactions.append(convert_transaction(item))

    return transactions


def get_transactions_by_dst(dst):
    transactions = []
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('transactions')

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
    print(transaction)
    if not transaction.signed:
        transaction.signed = True
    create_transaction(transaction)


def update_transaction(other):
    transaction = get_transaction_by_key(other.transaction_id)
    if transaction.signed != other.signed:
        transaction.signed = other.signed
    create_transaction(transaction)


def delete_transaction(key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('transactions')
    table.delete_item(
        Key={'transaction_id': key}
    )
