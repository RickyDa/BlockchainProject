import os
import requests
import re
import time
import boto3
import json
from apscheduler.schedulers.background import BackgroundScheduler
from botocore.exceptions import ClientError
from datetime import datetime
from globals import cfg
from utils.utils import *

sched = BackgroundScheduler()


def tick():
    print('Tick! The time is: %s' % datetime.now())


def transactions_to_file(block):
    file_name = datetime.now().strftime("%m/%d/%Y_%H:%M:%S")
    file_name = f"{re.sub(r'[,/:]', '_', file_name)}.txt"
    tids = []
    data = []
    for b in block:
      body = {}
      tid = b['transaction_id']['StringValue']
      body['id'] = tid
      body['src'] = b['src']['StringValue']
      body['dst'] = b['dst']['StringValue']
      body['amount'] = b['amount']['StringValue']
      data.append(body)
      tids.append(tid)
    #with open(file_name, "w") as f:
       # for b in block:
       #     tid = b['transaction_id']['StringValue']
        #    f.write(f"{tid}, \
             #       src: {b['src']['StringValue']}, \
             #       dst: {b['dst']['StringValue']}, \
             #        {}\n")
           # tids.append(tid)
    return file_name, data, tids


def upload_block(file_name, data, object_name=None, bucket_name=cfg.BUCKET_NAME_BLOCKS):
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:

        response = s3_client.put_object(Body=data, Bucket=bucket_name, Key=file_name)
    except ClientError as e:
        print(e)
        return False
    return True


def delete_transactions(tids):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(cfg.TRANSACTION_TABLE)
    for tid in tids:
        table.delete_item(Key={'transaction_id': tid})


def snapshot():
    if cfg.ID == cfg.LEADER_ID:
        snap_date = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        response = {"instances_list": get_instances()}
        for instance in response["instances_list"]:
            file_name = f"snapshot_{snap_date}.json"
            try:
                res = requests.get(f"http://{instance['DNS']}:{cfg.PORT}/getState")
                upload_block(f"{instance['DNS']}/{file_name}", data=str(res.json()), bucket_name=cfg.BUCKET_NAME_STATE)
            except Exception as e:
                print(e)


def add_block():
    if cfg.ID == cfg.LEADER_ID:
        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName=cfg.Q_NAME)

        response = [0]
        message_count = 0
        block = []

        while len(response) > 0 and message_count < cfg.TRANSACTION_LIMIT:
            response = queue.receive_messages(MessageAttributeNames=['All'])
            for message in response:

                if message.message_attributes is not None:
                    block.append(message.message_attributes)

                message.delete()
                message_count += 1

        if message_count > 0:
            block_name, data, tids = transactions_to_file(block)
            upload_block(block_name, str(data).replace("[","").replace("]",""))
            # delete_transactions(tids) # uncomment if u want to delete signed transactions
            print(f"{message_count} TRANSACTIONS SIGNED TO BLOCK")
        else:
            print("NO TRANSACTIONS")
    else:
        try:
            requests.get(f"http://{cfg.LEADER_DNS}:{cfg.PORT}/ping")
        except Exception as e:
            print(e)
            print('leader down, starting election')
            requests.get(f"http://{get_public_DNS()}:{cfg.PORT}/elect")


if __name__ == '__main__':
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        sched.add_job(tick, 'interval', seconds=10)
        sched.start()
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        print('CRON TASK STOPPED')
        sched.shutdown()
else:
    sched.add_job(add_block, 'interval', minutes=1)
    sched.add_job(snapshot, 'interval', minutes=2)
