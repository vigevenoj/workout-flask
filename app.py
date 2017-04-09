#! /usr/bin/env python
from flask import Flask, abort, jsonify, make_response, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, DATE, text
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


@app.route('/api/v1/runs/latest')
def get_latest_run():
    # "SELECT r.rdate, r.timeofday, r.distance, r.units, r.elapsed FROM runs r
    # where r.rdate = (SELECT MAX(r2.rdate) FROM runs r2)"
    abort(404)


@app.route('/api/v1/stats/last/<int:days>')
def last_x_days(days):
    if days is None or days <= 0:
        return bad_request
    today = datetime.date.today()
    x_day = today + datetime.timedelta(0 - days)
    runs = Run.query.filter(cast(Run.rdate, DATE) >= x_day).all()
    # TODO return total miles and duration for the time period
    result = RunSchema().dump(runs, many=True)
    return jsonify({'runs': result.data})


@app.route('/api/v1/stats/ytd')
def ytd():
    jan1 = datetime.date(year=datetime.date.today().year, month=1, day=1)
    sql = text('select sum(r.distance*uc.factor) as distance from runs r, '
               'unit_conversion uc where uc.from_u = r.units and uc.to_u = '
               ' :units and r.distance is not null and r.rdate >= :date')
    results = db.engine.execute(sql, {'units': 'miles', 'date': jan1})
    result = results.first()[0]
    resp = {'distance': result,
            'units': 'miles'}
    return jsonify({'ytd': resp})


@app.route('/api/v1/stats/yearly/<int:year>')
def yearly_stats(year):
    if year < 1900:
        abort(400)
    if year > datetime.date.today().year:
        abort(400)
    sql = text("SELECT count(distance_interval) as count, distance_interval "
               "FROM ( "
               "SELECT r.distance, r.units, "
               "CASE "
               "WHEN (r.distance*uc.factor) <= 1 THEN '1 mile or less' "
               "WHEN (r.distance*uc.factor) > 1 AND (r.distance*uc.factor) <= 3 THEN '1 - 3 miles' "
               "WHEN (r.distance*uc.factor) > 3 AND (r.distance*uc.factor) <= 5 THEN '3 - 5 miles' "
               "WHEN (r.distance*uc.factor) > 5 AND (r.distance*uc.factor) <= 10 THEN '5 - 10 miles' "
               "WHEN (r.distance*uc.factor) > 10 AND (r.distance*uc.factor) <= 15 THEN '10 - 15 miles' "
               "WHEN (r.distance*uc.factor) > 15 AND (r.distance*uc.factor) <= 20 THEN '15 - 20 miles' "
               "WHEN (r.distance*uc.factor) > 20 AND (r.distance*uc.factor) <= 25 THEN '20 - 25 miles' "
               "WHEN (r.distance*uc.factor) > 25 THEN 'over 25 miles' "
               "ELSE 'Other' "
               "END AS distance_interval "
               "FROM runs r, unit_conversion uc "
               "WHERE uc.from_u = r.units and uc.to_u = 'miles' "
               "AND r.distance IS NOT NULL and r.elapsed IS NOT NULL "
               "AND EXTRACT(YEAR from r.rdate) = :year "
               ") AS t "
               "GROUP BY distance_interval")
    results = db.engine.execute(sql, {'year': year})
    all_rows = results.fetchall()
    ranges = dict((interval, count) for count, interval in all_rows)
    return jsonify({'distance ranges' : ranges})


if __name__ == '__main__':
    app.run(debug=True)
