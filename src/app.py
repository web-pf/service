from flask import Flask, request
import random
import string

from .api import user

API_VERSION = 'v1'

app = Flask(__name__)
app.secret_key = ''.join(random.choices(
    string.ascii_letters + string.digits, k=64))


def createApiPrefix(append_path):
    print(f"/api/{API_VERSION}{append_path}")
    return f"/api/{API_VERSION}{append_path}"


def main():
    app.register_blueprint(user.api, url_prefix=createApiPrefix('/user'))
    app.debug = True
    app.run(host='0.0.0.0', port=4430)


if __name__ == '__main__':
    main()
