import boto3
import botocore
from botocore.exceptions import ClientError

class User:

    def __init__(self, user_email, first_name, last_name, password, amount):
        self.user_email = user_email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.amount = amount

    def __repr__(self):
        return f'user_email:{self.user_email}, ' \
               f'first_name:{self.first_name}, ' \
               f'last_name:{self.last_name}, ' \
               f'password:{self.password}, ' \
               f'ammount:{self.amount}'


def convert_user(item):
    try:
        user_email = list(item['user_email']['S'].values())[0]
        amount = int(list(item['amount']['N'].values())[0])
        first_name = list(item['first_name']['S'].values())[0]
        last_name = list(item['last_name']['S'].values())[0]
        password = item['password']['S']
    except:
        user_email = list(item['user_email'].values())[0]
        amount = int(list(item['amount'].values())[0])
        first_name = list(item['first_name'].values())[0]
        last_name = list(item['last_name'].values())[0]
        password = item['password']

    return User(user_email=user_email, first_name=first_name, last_name=last_name, amount=amount, password=password)


def create_user(user, table_name='users'):
  try:
      dynamodb = boto3.resource('dynamodb')
      table = dynamodb.Table(table_name)
      return table.put_item(Item=user.__dict__)
  except ClientError as ce:
    return None


def get_all_users():
  users = []
  try:
      dynamo_client = boto3.client('dynamodb')
      resp = dynamo_client.scan(TableName='users')
  
      for item in resp['Items']:
          users.append(convert_user(item))
  
      return users
  except ClientError as ce:
    return users


def convert_respons_to_user(item):
  try:
    user_email = item['user_email']['S']
    amount = int(item['amount']['N'])
    first_name = item['first_name']['S']
    last_name = item['last_name']['S']
    password = item['password']['S']
  except:
    user_email = item['user_email']
    amount = int(item['amount'])
    first_name = item['first_name']
    last_name = item['last_name']
    password = item['password']
    
  return User(user_email=user_email, first_name=first_name, last_name=last_name, amount=amount, password=password)



def get_users_by_key(key):
  try:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    response = table.get_item(Key={'user_email': key})
    return convert_respons_to_user(response['Item'])
  except ClientError as ce:
    return None


def update_user(u_user: User):
    try:
        user = get_users_by_key(u_user.user_email)

        if user.first_name != u_user.first_name:
            user.first_name = u_user.first_name

        if user.last_name != u_user.last_name:
            user.last_name = u_user.last_name

        if user.amount != u_user.amount:
            user.amount = u_user.amount

        if user.password != u_user.password:
            user.password = u_user.password

        create_user(user)
        return user
    except Exception as e:
        print(e)
        print('USER UPDATE FAILED')
        return u_user


def delete_user(key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    table.delete_item(
        Key={'user_email': key}
    )
