from flask import Blueprint
import json

api = Blueprint('user', __name__)


@api.route('/current')
def get_current():
    return json.dumps({
        "status": "REGISTERED"
    })
