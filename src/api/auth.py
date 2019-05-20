from flask import request, session, make_response
import json
from functools import wraps


def authenticate():
    def wrapper(func):
        @wraps(func)
        def wrapper_func():

            auth_token = request.cookies.get('auth_token')
            uid = session.get(auth_token)
            if uid:
                return func(uid)
            else:
                return make_response(json.dumps({
                    "error": True,
                    "msg": "Your token has timed out."
                }), 403)

        return wrapper_func

    return wrapper
