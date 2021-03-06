from flask import Flask, request
import random
import string
import datetime

from api import user, website, beacon, perf, error

API_VERSION = 'v1'

app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(seconds=120*60)
app.secret_key = ''.join(random.choices(
    string.ascii_letters + string.digits, k=64))


def create_api_prefix(append_path):
    return f"/api/{API_VERSION}{append_path}"

def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


def main():
    app.register_blueprint(user.api, url_prefix=create_api_prefix('/user'))
    app.register_blueprint(error.api, url_prefix=create_api_prefix('/error'))
    app.register_blueprint(beacon.api, url_prefix=create_api_prefix('/beacon'))
    app.register_blueprint(website.api, url_prefix=create_api_prefix('/website'))
    app.register_blueprint(perf.api, url_prefix=create_api_prefix('/perf'))
    app.debug = True
    app.after_request(after_request)
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
