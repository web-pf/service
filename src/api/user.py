from flask import Blueprint, request, session, make_response
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import json
from .db import client

platform_db = client['web_pf']

users_col = platform_db['users']
inv_code_col = platform_db['inv_codes']

api = Blueprint('user', __name__)


@api.route('/current', methods=['GET'])
def user_current():
    auth_token = request.cookies.get('auth_token')
    email = session.get(auth_token)
    if email:

        info = users_col.find_one({
            "email": email
        })

        return json.dumps({
            "email": info['email']
        })
    else:
        return make_response(json.dumps({
            "error": True
        }))


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
    passwords_hash = users_col.find_one({
        "email": email
    })['passwords']
    if check_password_hash(passwords_hash, passwords):
        response = make_response(json.dumps({
            "error": False
        }))
        token = secrets.token_hex(64)
        session[token] = email
        session.permanent = True
        response.set_cookie('auth_token', token)
        return response


@api.route('/register', methods=['PUT'])
def user_register():
    email = request.form['email']
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
                "email": email,
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
