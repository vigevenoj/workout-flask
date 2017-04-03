#! /usr/bin/env python
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask import abort
# import yaml

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello world"


@app.route('/running/api/v1/runs', methods=['GET'])
def get_runs():
    # for now, abort with a 501 not implemented
    abort(501)


@app.route('/running/api/v1/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    # for now abort with a 501 not implemented
    abort(501)

if __name__ == '__main__':
    app.run(debug=True)
