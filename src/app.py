from flask import Flask

app = Flask(__name__)


@app.route('/<pagename>', methods = ['GET'])
def hello_world(pagename):
    return pagename
    

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=4430)

