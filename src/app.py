from flask import Flask, request
import random
import string
import datetime

from api import user, website

API_VERSION = 'v1'

app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(seconds=120*60)
app.secret_key = ''.join(random.choices(
    string.ascii_letters + string.digits, k=64))


def create_api_prefix(append_path):
    return f"/api/{API_VERSION}{append_path}"


def main():
    app.register_blueprint(user.api, url_prefix=create_api_prefix('/user'))
    app.register_blueprint(website.api, url_prefix=create_api_prefix('/website'))
    app.debug = True
    app.run(host='0.0.0.0', port=4430)


if __name__ == '__main__':
    main()
