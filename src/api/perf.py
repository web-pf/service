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


def gen_item(record, indicator):
    return {
        "type": indicator,
        "date": time.strftime("%Y-%m-%d,%H:%M:%S", time.gmtime(record['timestamp']/1000)),
        "value": record['record'][indicator]
    }


def get_trending(raw_data, indicators):
    return [gen_item(record, indicator) for record in raw_data for indicator in indicators.split(',')]


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
            ''' % (start_date, end_date)
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


def stash_resource(stash, record, resource_record):
    name = resource_record['name']
    mean_required_indicators = ['dns', 'tcp',
                                'request', 'response', 'duration']

    if name not in stash:
        stash[name] = {}
    for key in resource_record.keys():
        if key in mean_required_indicators:
            if key not in stash[name]:
                stash[name][key] = [resource_record[key]]
            else:
                stash[name][key].append(resource_record[key])
        else:
            if key not in stash[name]:
                stash[name][key] = resource_record[key]


def get_resource_mean(raw_data):
    def handle(resource_item: dict):
        for key, value in resource_item.items():
            if isinstance(value, list):
                resource_item[key] = mean(value)
        return resource_item

    stash = {}
    [stash_resource(stash, record, resource_record)
     for record in raw_data for resource_record in record['record']]

    result = [handle(resource_item) for resource_item in stash.values()]
    result.sort(key=lambda item: item['duration'])

    return result[0:15]


@api.route('/resource', methods=['GET'])
@authenticate()
def perf_resource(uid):
    app_id: str = request.args.get('appId')
    start_date: int = request.args.get('startDate')
    end_date: int = request.args.get('endDate')
    is_legal_request = website_col.find_one({
        'appId': app_id,
        'uid': uid
    })

    if is_legal_request:
        resource_timing_perf_col = platform_db[f'app_{app_id}'].find(
            {'name': 'resource_timing',
             '$where': '''
            function(){
                const timestamp = this.timestamp/1000
                if(timestamp >= %s && timestamp <= %s) return true
                else return false
            }
            ''' % (start_date, end_date)
             }, {"_id": 0})

        return make_response(json.dumps({
            "error": False,
            "content": get_resource_mean(resource_timing_perf_col)
        }))

    else:
        return make_response(json.dumps({
            "error": False,
            "msg": "this app id is not yours."
        }), 404)
