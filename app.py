from flask import Flask
from flask import request, Response
import user_controller as uc

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def index():
    try:
        json_user = request.get_json()
        new_user = uc.User(user_email=json_user['user_email'],
                           first_name=json_user['first_name'],
                           last_name=json_user['last_name'],
                           amount=int(json_user['ammount']),
                           password=json_user['password'])
        uc.create_user(new_user)
        return Response(status=200)
    except Exception as e:
        return Response(status=500)


@app.route('/login', methods=['POST'])
def login():
    key, pw = request.get_json()['user_email'], request.get_json()['password']
    user = uc.get_users_by_key(key)
    print(type(pw), type(user.password))
    if pw == user.password:
        return Response(status=200)
    return Response(status=401)


if __name__ == '__main__':
    app.run()