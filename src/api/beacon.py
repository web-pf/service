from flask import Blueprint, request, session, make_response
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import json
import shortuuid
from .db import client
from .auth import authenticate
from .util.db import get_next_seq


platform_db = client['web_pf']
website_col = platform_db['websites']
counters_col = platform_db['counters']

api = Blueprint('beacon', __name__)


def save_beacon(record):
    print(request.remote_addr)
    app_id = record['appId']
    beacon_name = record['name']
    beacon_record = record['record']
    timestamp = record['timestamp']
    platform_db[f"app_{app_id}"].insert_one({
        "timestamp": int(timestamp),
        "name": beacon_name,
        "record": beacon_record
    })
    

@api.route('', methods=['PUT'])
def upload_beacon():
    content = request.json
    validated_app_id = {}

    for single_beacon_record_string in content:
        single_beacon_record = json.loads(single_beacon_record_string)
        app_id = single_beacon_record['appId']

        if app_id in validated_app_id:
            save_beacon(single_beacon_record)

        else:
            website_record = website_col.find_one({
                "appId": app_id
            })

            if website_record:
                validated_app_id[app_id] = True
                save_beacon(single_beacon_record)
            else:
                return make_response(json.dumps({
                    "error": True,
                    "msg": "app id not found"
                }), 404)
    return json.dumps({
        "error": False
    })
