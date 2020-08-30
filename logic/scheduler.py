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
    with open(file_name, "w") as f:
        for b in block:
            tid = b['transaction_id']['StringValue']
            f.write(f"{tid}, \
                    src: {b['src']['StringValue']}, \
                    dst: {b['dst']['StringValue']}, \
                    amount: {b['amount']['StringValue']}\n")
            tids.append(tid)
    return file_name, tids


def upload_block(file_name, object_name=None, bucket_name=cfg.BUCKET_NAME_BLOCKS):
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
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
    response = {"instances_list": get_instances()}
    leader_cfg = cfg.config_to_dict()
    # Save Leader cfg to json
    save_json_to_file(leader_cfg, cfg.DNS)
    upload_block(f"{cfg.LEADER_DNS}.json", bucket_name=cfg.BUCKET_NAME_STATE)

    # Save instances configs to json
    for instance in response["instances_list"]:
        if instance['DNS'] is not cfg.LEADER_DNS:
            res = requests.get(f"http://{instance['DNS']}:{cfg.PORT}/getState")
            save_json_to_file(res, instance['DNS'])
            upload_block(f"{instance['DNS']}.json", bucket_name=cfg.BUCKET_NAME_STATE)


def save_json_to_file(config_file, file_name):
    with open(f'{file_name}.json', 'w') as f:
        json.dump(config_file, f, ensure_ascii=False)


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
            block_name, tids = transactions_to_file(block)
            upload_block(block_name)
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
    sched.add_job(snapshot, 'interval', seconds=5)