#! /usr/bin/env python
from flask import Flask, abort, jsonify, make_response, request, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from models import *
# import yaml
# from pprint import pprint

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
    runs = Run.query.all()
    run_schema = RunSchema()
    result = run_schema.dump(runs)
    return jsonify({'runs': result.data})


@app.route('/running/api/v1/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    this_run = Run.query.get(run_id)
    if not this_run:
        abort(404)
    run_schema = RunSchema()
    result = run_schema.dump(this_run)
    return jsonify({'run': result.data})


@app.route('/running/api/v1/runs', methods=['POST'])
# @auth.login_required
def create_run():
    if not request.json:
        abort(400)
    rdate = request.json['rdate']
    timeofday = request.json['timeofday']
    distance = request.json['distance']
    units = request.json['units']
    elapsed = request.json['elapsed']
#    effort = request.json['effort']
    comment = request.json['comment']
    this_run = Run(rdate=rdate, timeofday=timeofday, distance=distance,
                   units=units, elapsed=elapsed, effort="", comment=comment)
    db.session.add(this_run)
    db.session.commit()
    return (jsonify({'run': this_run.rdate}), 201,
            {'Location': url_for('get_run', run_id=this_run.runid,
                                 _external=True)})

if __name__ == '__main__':
    app.run(debug=True)
