from flask import Flask
from flask import request, Response
from utils import *
import requests
import user_controller as uc

PORT = 5000
app = Flask(__name__)


@app.route('/register', methods=['POST'])
def index():
    try:
        json_user = request.get_json()
        new_user = uc.User(user_email=json_user['user_email'].lower(),
                           first_name=json_user['first_name'],
                           last_name=json_user['last_name'],
                           amount=json_user['ammount'],
                           password=json_user['password'])
        uc.create_user(new_user)
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/login', methods=['POST'])
def login():
    key, pw = request.get_json()['user_email'].lower(), request.get_json()['password']
    user = uc.get_users_by_key(key)
    if pw == user.password:
        return Response(status=200)
    return Response(status=401)


"""
############################# LEADER ELECTION ###################################
### The leader is the one the get not responses OR has the highest rank (ID)  ###
https://www.cs.colostate.edu/~cs551/CourseNotes/Synchronization/BullyExample.html
"""
ID = get_instance_ID()
LEADER_ID = ''
LEADER_DNS = ''


@app.route('/getleader', methods=['GET'])
def get_leader():
    return {'LEADER_ID': str(LEADER_ID), 'LEADER_DNS': str(LEADER_DNS)}


@app.route('/leader', methods=['POST'])
def assign_leader():
    global LEADER_ID, LEADER_DNS
    imd = request.form
    LEADER_ID = imd['leader']
    LEADER_DNS = imd['PUBLIC_DNS']
    print(f"The Leader is: ID - {LEADER_ID} on {LEADER_DNS}")
    return Response(status=200)


def broadcast(nodes, path, payload):
    response_count = 0

    for node in nodes:
        try:
            if path == 'leader':
                requests.post(f"http://{node['DNS']}:{PORT}/{path}", data=payload)
            else:
                requests.get(f"http://{node['DNS']}:{PORT}/{path}", data=payload)
            response_count += 1
        except Exception as e:
            print(e)
    return response_count


@app.route('/elect', methods=['GET', 'POST'])
def elect():
    """
    starts bully leader election between nodes
    """
    if request.method == 'GET':
        nodes = get_instances()
        higher_ranks = find_higher_ranks(nodes=nodes, my_rank=ID)
        if len(higher_ranks) == 0:
            print('No higher ranks Im the leader')
            broadcast(nodes=nodes, path="leader", payload={'leader': ID,
                                                           'PUBLIC_DNS': get_public_DNS()})
        else:
            print('Wait for responses')
            response_count = broadcast(nodes=higher_ranks, path="elect", payload={'leader': ID})
            if response_count == 0:
                print('No responses Im the leader')
                broadcast(nodes=nodes, path="leader", payload={'leader': ID,
                                                               'PUBLIC_DNS': get_public_DNS()})
    return Response(status=200)


"""
############################# LEADER ELECTION ###################################
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True)  # on ec2 host='0.0.0.0', on local host='localhost'

# APP
# Leader Election - ricky Done.
# TODO:
#   Client side - login/ register, User API- dorel
#   Transaction API - itay
#   Client side - transcation
#   master


# Create user
'''
{
	"user_email": "rickyrIckYY@mail.com",
	"first_name":"ricky",
	"last_name":"dani",
	"ammount":3000,
	"password": "123456789"
}
'''

# login
'''
{
    "user_email" : "ricky@gmail.com",
    "password" : "1234567"
}
'''
