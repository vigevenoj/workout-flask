#! /usr/bin/env python
from flask import Flask, abort, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from models import *
# import yaml

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    return "Hello world\n"


@app.route('/running/api/v1/runs', methods=['GET'])
def get_runs():
    return jsonify({'runs': Run.query.all()})
    # for now, abort with a 501 not implemented
    abort(501)


@app.route('/running/api/v1/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    # for now abort with a 501 not implemented
    abort(404)

if __name__ == '__main__':
    app.run(debug=True)
