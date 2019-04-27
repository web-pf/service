from flask import Blueprint, request, session, make_response
import json
from .db import client

platform_db = client['web_pf']

users_col = platform_db['users']
inv_code_col = platform_db['inv_codes']

api = Blueprint('user', __name__)


@api.route('/current', methods=['GET'])
def user_current():
    email = request.args.get('email')

    auth_token = request.cookies.get('auth_token')

    return json.dumps({
        "status": 'UNREGISTERED'
    })


@api.route('/status', methods=['GET'])
def user_current():
    email = request.args.get('email')
    if not email:
        return make_response('', 422)
    else:
        user_result = users_col.find({
            "email": email
        })
        if len(user_result) == 0:
            return json.dumps({
                "status": "UNREGISTERED"
            })
        else:
            return json.dumps({
                "status": "REGISTERED"
            })


@api.route('/login', methods=['POST'])
def user_login():
    email = request.form['email']
    passwords = request.form['passwords']


@api.route('/register', methods=['PUT'])
def user_register():
    email = request.form['email']
    passwords = request.form['passwords']
    invitation_code = request.form['invitationCode']
    user_result = users_col.find({
        "email": email
    })
    inv_code_result = inv_code_col.find({
        "code": invitation_code
    }).where("this.times > 0")

    print(list(user_result))
    print(list(inv_code_result))

    return json.dumps({

    })
