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


def convert_perf_nav_timing(raw_data: [dict]):

    dns = get_timing_mean(raw_data, 'dnsLookUpTiming')
    tcp = get_timing_mean(raw_data, 'tcpTiming')
    request = get_timing_mean(raw_data, 'requestHandlingTiming')
    dom = get_timing_mean(raw_data, 'domProcessingTiming')
    t_await = get_timing_mean(
        raw_data, 'totalRenderingTiming') - dom - dns - tcp - request

    return [
        {
            "value": dns,
            "type": "DNS lookup"
        },
        {
            "value": tcp,
            "type": "TCP"
        },
        {
            "value": request,
            "type": "Request handling"
        },
        {
            "value": dom,
            "type": "DOM Processing"
        }, {
            "value": t_await,
            "type": "Await"
        }
    ]


def get_nav_timing_trending(raw_data):
    result = []
    for record in raw_data:
        timestamp = time.strftime("%Y-%m-%d,%H:%M:%S", time.gmtime(record['timestamp']/1000))
        totalTiming = record['record']['totalRenderingTiming']

        result.append({"date": timestamp, "time used": totalTiming})
    return result


@api.route('/nav_timing_sharing', methods=['GET'])
@authenticate()
def perf_nav_sharing(uid):
    app_id: str = request.args.get('appId')
    is_legal_request = website_col.find_one({
        'appId': app_id,
        'uid': uid
    })

    if is_legal_request:
        nav_timing_perf_col = platform_db[f'app_{app_id}'].find(
            {'name': 'nav_timing'}, {"record": 1, "_id": 0})

        return make_response(json.dumps({
            "error": False,
            "content": convert_perf_nav_timing(list(nav_timing_perf_col))
        }))

    else:
        return make_response(json.dumps({
            "error": False,
            "msg": "this app id is not yours."
        }), 404)


@api.route('/nav_timing_trending', methods=['GET'])
@authenticate()
def perf_nav_trending(uid):
    app_id: str = request.args.get('appId')
    is_legal_request = website_col.find_one({
        'appId': app_id,
        'uid': uid
    })

    if is_legal_request:
        nav_timing_perf_col = platform_db[f'app_{app_id}'].find(
            {'name': 'nav_timing'}, {"_id": 0})

        return make_response(json.dumps({
            "error": False,
            "content": get_nav_timing_trending(list(nav_timing_perf_col))
        }))

    else:
        return make_response(json.dumps({
            "error": False,
            "msg": "this app id is not yours."
        }), 404)
