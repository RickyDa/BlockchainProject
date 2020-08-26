from flask import Flask, render_template, flash
from flask import request, Response
import requests
from logic import user_controller as uc, transaction_controller as tc
from utils.utils import *
from utils.validation import ensure_email_validation
from globals import cfg

app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            key, pw = request.form['user_email'].lower(), request.form['password']
            user = uc.get_users_by_key(key)
            if pw == user.password:
                return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(key))
            return Response(status=401)
        return render_template('index.html')
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/allusers', methods=['GET'])
def users():
    try:
        mock_data = [(uc.User(user_email="dorel@gamil.com", first_name="dorel", last_name="shoshany", password="pass",
                              amount=20))]
        return render_template('showAllUser.html', users=mock_data)  # uc.get_all_users())
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/myTransactions', methods=['GET', 'POST'])
def my_transactions():
    try:
        # if this is post -> create new one, if this is get -> just show all my transactions
        if request.method == 'POST':
            # TODO: valid form + save the src as a global and not take it from the html!
            new_transaction = tc.Transaction(src=request.form['src'].lower(),
                                             dst=request.form['dst'],
                                             amount=request.form['amount'])
            tc.create_transaction(new_transaction)
            return render_template('myTransactions.html')
        return render_template('myTransactions.html', transactions=tc.get_sigh_transactions("dddd"))
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/transactionsToSign', methods=['GET', 'POST'])
def transactions_to_sign():
    try:
        if request.method == 'POST':
            return "ok", 200  # TODO: implement Sign transactions
        mock_data = [(tc.Transaction("ricky@gamil.com", "dorel@gamil.com", 20, False))]
        return render_template('transactionsToSigh.html',
                               transactions=mock_data)  # transactions=tc.get_transactions_by_dst("dddd"))
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'POST':
            user_email = request.form['user_email'].lower()
            email_is_valid = ensure_email_validation(user_email)
            if email_is_valid is False:
                flash('The email is not valid')
                return render_template('register.html')
            else:
                new_user = uc.User(user_email=user_email,
                                   first_name=request.form['first_name'],
                                   last_name=request.form['last_name'],
                                   amount=request.form['ammount'],
                                   password=request.form['password'])
                uc.create_user(new_user)
                return render_template('myTransactions.html')
        return render_template('register.html')
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        if request.method == 'POST':
            key, pw = request.form['user_email'].lower(), request.form['password']
            email_is_valid = ensure_email_validation(key)
            if email_is_valid is False:
                flash('The email is not valid')
                return render_template('login.html')
            user = uc.get_users_by_key(key)
            if pw == user.password:
                return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(key))
            else:
                flash('bad email or password')
                return render_template('login.html')
        return render_template('login.html')
    except Exception as e:
        print(e)
        return Response(status=500)


"""
################################## LEADER ELECTION ########################################
########   The leader is the one gets no responses OR has the highest rank (ID)    ########
###  https://www.cs.colostate.edu/~cs551/CourseNotes/Synchronization/BullyExample.html  ###
###########################################################################################
"""


@app.route('/ping', methods=['GET'])
def ping():
    return Response(status=200)


@app.route('/getleader', methods=['GET'])
def get_leader():
    return {'LEADER_ID': str(cfg.LEADER_ID), 'LEADER_DNS': str(cfg.LEADER_DNS)}


@app.route('/leader', methods=['POST'])
def assign_leader():
    imd = request.form
    cfg.LEADER_ID = imd['leader']
    cfg.LEADER_DNS = imd['PUBLIC_DNS']
    print(f"The Leader is: ID - {cfg.LEADER_ID} on {cfg.LEADER_DNS}")
    return Response(status=200)


def broadcast(nodes, path, payload):
    response_count = 0

    for node in nodes:
        try:
            if path == 'leader':
                requests.post(f"http://{node['DNS']}:{cfg.PORT}/{path}", data=payload)
            else:
                requests.get(f"http://{node['DNS']}:{cfg.PORT}/{path}", data=payload)
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
        higher_ranks = find_higher_ranks(nodes=nodes, my_rank=cfg.ID)
        if len(higher_ranks) == 0:
            print('No higher ranks Im the leader')
            broadcast(nodes=nodes, path="leader", payload={'leader': cfg.ID,
                                                           'PUBLIC_DNS': get_public_DNS()})
        else:
            print('Wait for responses')
            response_count = broadcast(nodes=higher_ranks, path="elect", payload={'leader': cfg.ID})
            if response_count == 0:
                print('No responses Im the leader')
                broadcast(nodes=nodes, path="leader", payload={'leader': cfg.ID,
                                                               'PUBLIC_DNS': get_public_DNS()})
    return Response(status=200)

from scheduler import sched, add_block
sched.add_job(add_block, 'interval', minutes=1)
sched.start()
"""
############################# LEADER ELECTION ###################################
"""
if __name__ == '__main__':
    # app.run( port=PORT, threaded=True)
    app.run(host='0.0.0.0', port=cfg.PORT, threaded=True)  # on ec2 host='0.0.0.0', on local host='localhost'

# APP
# Leader Election - ricky Done.
# TODO:
#   User API- dorel
#   Transaction API - itay
#   Client side - transcation - almost done :)
#   master - Ricky


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
