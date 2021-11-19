from flask import Flask
from router import query
app = Flask(__name__)
app.register_blueprint(query)
@app.route('/api/v7/hello-world-7')
def hello_world():
    return 'Hello world 7'
