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


api = Blueprint('perf', __name__)


def get_timing_mean(raw_data: [dict], item_name: str):
    return mean([dic['record'][item_name] for dic in raw_data])


def convert_perf_nav_timing(raw_data: [dict], indicators:str):
    res = []
    for indicator in indicators.split(','):
        res.append({
            "value": get_timing_mean(raw_data, indicator),
            "type": indicator
        })
    
    return res



def get_trending(raw_data, indicators):
    result = {}
    indicators = indicators.split(',')
    for record in raw_data:
        for indicator in indicators:
            if indicator not in result:
                result[indicator] = []
            result[indicator].append({
                "date": time.strftime("%Y-%m-%d,%H:%M:%S", time.gmtime(record['timestamp']/1000)),
                "value": record['record'][indicator]
            })
    return result


@api.route('/trending', methods=['GET'])
@authenticate()
def perf_nav_trending(uid):
    app_id: str = request.args.get('appId')
    start_date: int = request.args.get('startDate')
    end_date: int = request.args.get('endDate')
    indicators: str = request.args.get('indicators')
    is_legal_request = website_col.find_one({
        'appId': app_id,
        'uid': uid
    })

    if is_legal_request:
        nav_timing_perf_col = platform_db[f'app_{app_id}'].find(
            {'name': 'nav_timing',
            '$where': '''
            function(){
                const timestamp = this.timestamp/1000
                if(timestamp >= %s && timestamp <= %s) return true
                else return false
            }
            '''%(start_date, end_date)
            }, {"_id": 0})

        return make_response(json.dumps({
            "error": False,
            "content": get_trending(list(nav_timing_perf_col), indicators)
        }))

    else:
        return make_response(json.dumps({
            "error": False,
            "msg": "this app id is not yours."
        }), 404)
