from flask import Blueprint, request, session, make_response
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import json
from .db import client
from .auth import authenticate
from .util.db import get_next_seq

platform_db = client['web_pf']

users_col = platform_db['users']
counters_col = platform_db['counters']
inv_code_col = platform_db['inv_codes']

api = Blueprint('user', __name__)


@api.route('/current', methods=['GET'])
@authenticate()
def user_current(uid):
    info = users_col.find_one({
        "uid": uid
    })

    return json.dumps({
        "uid": info['uid'],
        "email": info['email'],
        "nickname": info['nickname']
    })


@api.route('/status', methods=['GET'])
def user_status():
    email = request.args.get('email')
    if not email:
        return make_response('', 422)
    else:
        user_result = users_col.find({
            "email": email
        })
        if user_result.count() == 0:
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

    user_info = users_col.find_one({
        "email": email
    })

    passwords_hash = user_info['passwords']
    nickname = user_info['nickname']
    uid = user_info['uid']

    if check_password_hash(passwords_hash, passwords):
        response = make_response(json.dumps({
            "error": False,
            "email": email,
            "uid": uid,
            "nickname": nickname,

        }))
        token = secrets.token_hex(64)
        session[token] = uid
        session.permanent = True
        response.set_cookie('auth_token', token)
        return response


@api.route('/register', methods=['PUT'])
def user_register():
    email = request.form['email']
    nickname = request.form['nickname']
    passwords = request.form['passwords']
    invitation_code = request.form['invitationCode']

    email_is_available = users_col.find({
        "email": email
    }).count() == 0

    if email_is_available:
        inv_code_result = inv_code_col.find_and_modify({
            "code": invitation_code,
            "$where": "this.remaining > 0"
        }, {
            "$inc": {"remaining": -1}
        })

        if inv_code_result:
            users_col.insert_one({
                "uid": get_next_seq(counters_col, 'userId'),
                "email": email,
                "nickname": nickname,
                "used_inv_code": invitation_code,
                "passwords": generate_password_hash(passwords)
            })
            return json.dumps({
                "error": False,
                "msg": "Account created."
            })

        else:
            return json.dumps({
                "error": True,
                "msg": "Your invitation code is wrong or its remaining number has been used up."
            })

    else:
        return json.dumps({
            "error": True,
            "msg": "This email address has been registered."
        })
