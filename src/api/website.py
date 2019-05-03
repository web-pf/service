from flask import Blueprint, request, session, make_response
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import json
from .db import client
from .auth import authenticate
from .util.db import get_next_seq


platform_db = client['web_pf']
website_col = platform_db['website']
counters_col = platform_db['counters']

api = Blueprint('website', __name__)


@api.route('', methods=['PUT'])
@authenticate()
def website_register(uid):
    content = request.json
    url = content['websiteUrl']
    name = content['websiteName']
    description = content['websiteDescription']

    next_website_id = get_next_seq(counters_col, 'websiteId')

    website_col.insert_one({
        "websiteId": next_website_id,
        "uid": uid,
        "url": url,
        "name": name,
        "description": description
    })
    
    return json.dumps({
      "error": False,
      "websiteId": next_website_id
    })
