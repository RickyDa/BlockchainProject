import requests
from flask import Flask, render_template, flash
from flask import request, Response
from logic import user_controller as uc, transaction_controller as tc
from utils.utils import *
from utils.validation import ensure_email_validation
from globals import cfg, consts
from logic.scheduler import sched

app = Flask(__name__)
app.secret_key = 'super secret key'
user_logged_in = None
user_email = None


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
        return render_template('showAllUser.html', users=uc.get_all_users())
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/getState', methods=['GET'])
def get_state():
    try:
        if request.method == 'GET':
            Response.data = cfg.config_to_json()
            return Response.data
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/updateState', methods=['POST'])
def update_state():
    imd = request.json
    with open("snapshot.txt", "a") as f:
        f.write(f"{str(imd['snapshot'])}\n")
    return Response(status=200)


@app.route('/myTransactions', methods=['GET', 'POST'])
def my_transactions():
    try:
        global user_email
        global user_logged_in
        if user_email is None:
            flash(consts.MUST_LOGIN_MSG)
            return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(user_email))
        # if this is post -> create new one, if this is get -> just show all my transactions
        if request.method == 'POST':
            # TODO: valid form + save the src as a global and not take it from the html!
            receiver_email = request.form['receiver_email']
            my_email = user_email
            amount = int(request.form['amount'])
            if user_logged_in.amount < amount:
                flash(consts.NOT_ENOUGH_AMOUNT)
                return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(user_email))
            new_transaction = tc.Transaction(my_email, receiver_email, amount)
            save_transaction = tc.create_transaction(new_transaction)
            if save_transaction is None:
                flash(consts.TRANSACTIONS_TABLE_MSG)
            if user_logged_in is not None:
                user_email = user_logged_in.user_email
            flash(consts.TRANSACTION_CREATED_MSG)
            return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(user_email))
        return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(user_email))
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/transactionsToSign', methods=['GET', 'POST'])
def transactions_to_sign():
    try:
        global user_email
        global user_logged_in
        if user_logged_in is not None:
            user_email = user_logged_in.user_email
        if user_email is None:
            flash(consts.MUST_LOGIN_MSG)
            return render_template('myTransactions.html', transactions=tc.get_sigh_transactions(user_email))
        transactions = tc.get_transactions_by_dst(user_email)
        if transactions is None:
            flash(consts.TRANSACTIONS_TABLE_MSG)
            return render_template('transactionsToSigh.html',
                                   transactions=transactions)
        if request.method == 'POST':
            transaction_id_from_request = request.form["t"]
            transaction_id = transaction_id_from_request.replace("transaction_id:", '')
            transaction = tc.update_transaction_by_id(transaction_id)
            tc.send_transaction(transaction)
            uc.transfer_tokens(transaction.src, transaction.dst, transaction.amount)
            flash(consts.TRANSACTION_SIGNED_MSG)
            return render_template('transactionsToSigh.html',
                                   transactions=tc.get_transactions_by_dst(user_email))
        return render_template('transactionsToSigh.html',
                               transactions=transactions)
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        global user_logged_in
        global user_email
        if request.method == 'POST':
            user_email = request.form['user_email'].lower()
            email_is_valid = ensure_email_validation(user_email)
            if email_is_valid is False:
                flash(consts.EMAIL_MSG)
                return render_template('register.html')
            else:
                new_user = uc.User(user_email=user_email,
                                   first_name=request.form['first_name'],
                                   last_name=request.form['last_name'],
                                   amount=request.form['ammount'],
                                   password=request.form['password'])
                save_user = uc.create_user(new_user)
                if save_user is None:
                    flash('The users table is not exist')
                    return render_template('register.html')
                return render_template('register.html')
        return render_template('register.html')
    except Exception as e:
        print(e)
        return Response(status=500)


@app.route('/login', methods=['POST', 'GET'])
def login():
    global user_logged_in
    global user_email
    try:
        if request.method == 'POST':
            key, pw = request.form['user_email'].lower(), request.form['password']
            email_is_valid = ensure_email_validation(key)
            if email_is_valid is False:
                flash(consts.EMAIL_MSG)
                return render_template('login.html')
            user = uc.get_users_by_key(key)
            if user is None:
                flash(consts.USER_TABLE_MSG)
                return render_template('login.html')
            if pw == user.password:
                user_logged_in = user
                user_email = user_logged_in.user_email
                return render_template('myTransactions.html', transactions=[])  # tc.get_sigh_transactions(key))
            else:
                flash(consts.FAILED_LOGIN_MSG)
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


sched.start()
"""
############################# LEADER ELECTION ###################################
"""


@app.route('/updateblocks', methods=['POST'])
def update():
    imd = request.json
    with open("blocks.txt", "a") as f:
        f.write(f"{str(imd['block'])}\n")
    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=cfg.PORT, threaded=True)  # on ec2 host='0.0.0.0', on local host='localhost'
