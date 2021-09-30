from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world-7')
def hello_world():
    return 'Hello world 7'
