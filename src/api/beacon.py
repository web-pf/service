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
    app_id = record['appId']
    beacon_name = record['name']
    beacon_record = record['record']
    platform_db[f"app_{app_id}"].insertOne({
      "name": beacon_name,
      "record": beacon_record
    })


@api.route('', methods=['POST'])
def website_register_info(uid):
    content = request.json
    validated_app_id = {}

    for single_beacon_record in content:
        app_id = single_beacon_record['appId']

        if validated_app_id[app_id]:
            save_beacon(single_beacon_record)

        else:
            website_record = website_col.find_one({
                "appId": app_id
            })

            if website_record:
                validated_app_id[app_id] = True
                save_beacon(single_beacon_record)
