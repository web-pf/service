from flask import Blueprint, request, session, make_response
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import json
import shortuuid
import time
from numpy import mean
from .db import client
from .auth import authenticate
from .util.db import get_next_seq


platform_db = client['web_pf']
website_col = platform_db['websites']
counters_col = platform_db['counters']


api = Blueprint('error', __name__)

def create_errors_view(errors: list):
    if not len(errors):
        return []
    res = [errors[0]]
    res[0]['timestamp'] = [res[0]['timestamp']]
    for error in errors[1:]:
        if(res[-1]['record'] == error['record']):
            res[-1]['timestamp'].append(error['timestamp'])
        else:
            error['timestamp'] = [error['timestamp']]
            res.append(error)
    res.sort(key=(lambda item:item['timestamp'][-1]),reverse=True)

    return res


def get_error_list(uid: int, limit: int):
    app_id: str = request.args.get('appId')
    start_date: int = request.args.get('startDate') or '0'
    end_date: int = request.args.get('endDate') or str(time.time())
    is_legal_request = website_col.find_one({
        'appId': app_id,
        'uid': uid
    })

    if is_legal_request:
        error_col = platform_db[f'app_{app_id}'].find(
            {'name': 'error',
             '$where': '''
            function(){
                const timestamp = this.timestamp/1000
                if(timestamp >= %s && timestamp <= %s) return true
                else return false
            }
            ''' % (start_date, end_date)
             }, {"_id": 0}).limit(limit)

        return make_response(json.dumps({
            "error": False,
            "content": create_errors_view(list(error_col))
        }))

    else:
        return make_response(json.dumps({
            "error": False,
            "msg": "this app id is not yours."
        }), 404)


@api.route('/recent', methods=['GET'])
@authenticate()
def error_list_recent(uid):
    return get_error_list(uid, 5)


@api.route('/list', methods=['GET'])
@authenticate()
def error_list(uid):
    return get_error_list(uid, 100)
