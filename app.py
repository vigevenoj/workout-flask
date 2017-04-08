#! /usr/bin/env python
from flask import Flask, abort, jsonify, make_response, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, DATE
import os
from models import *
import datetime

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


@app.route('/api/v1/runs', methods=['GET'])
def get_runs():
    runs = Run.query.all()
    result = RunSchema().dump(runs, many=True)
    return jsonify({'runs': result.data})


@app.route('/api/v1/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    this_run = Run.query.get(run_id)
    if not this_run:
        abort(404)
    result = RunSchema().dump(this_run)
    return jsonify({'run': result.data})


@app.route('/api/v1/runs', methods=['POST'])
def create_run():
    json_data = request.get_json()
    if not json_data:
        abort(400)
    # Validate the input and deserialize it from the json body
    data, errors = RunSchema().load(json_data, partial=True)
    if errors:
        return jsonify(errors), 400
    if 'effort' in data:
        effort = data['effort']
    else:
        effort = ""
    if 'comment' in data:
        comment = data['comment']
    else:
        comment = ""
    run = Run(
        rdate=data['rdate'],
        timeofday=data['timeofday'],
        distance=data['distance'],
        elapsed=data['elapsed'],
        effort=effort,
        comment=comment,
    )
    db.session.add(run)
    db.session.commit()
    return (jsonify({'run': RunSchema().dump(run)}), 201,
            {'Location': url_for('get_run', run_id=run.runid,
                                 _external=True)})


@app.route('/api/v1/stats/last/<int:days>')
def last_x_days(days):
    if days is None or days <= 0:
        return bad_request
    today = datetime.date.today()
    x_day = today + datetime.timedelta(0-days)
    runs = Run.query.filter(cast(Run.rdate, DATE) >= x_day).all()
    result = RunSchema().dump(runs, many=True)
    return jsonify({'runs': result.data})

if __name__ == '__main__':
    app.run(debug=True)
