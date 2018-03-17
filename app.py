#! /usr/bin/env python
from flask import Flask, abort, jsonify, make_response, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, DATE, text
from sqlalchemy.exc import SQLAlchemyError
import os
from models import *  # Run, RunSchema
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


@app.route('/runs', methods=['GET'])
def get_runs():
    """Return a list of runs"""
    runs = Run.query.all()
    result = RunSchema().dump(runs, many=True)
    return jsonify({'runs': result.data})


@app.route('/runs/<int:run_id>', methods=['GET'])
def get_run(run_id):
    """Return the specified run"""
    this_run = Run.query.get(run_id)
    if not this_run:
        abort(404)
    result = RunSchema().dump(this_run)
    return jsonify({'run': result.data})


@app.route('/runs/<int:run_id>', methods=['DELETE'])
def delete_run(run_id):
    """Delete the specified run"""
    run = db.session.query(Run).filter_by(runid=run_id).first()
    if run is None:
        return not_found(run_id)
    try:
        db.session.delete(run)
        db.session.commit()
        response = make_response()
        response.status_code = 204
        return response
    except SQLAlchemyError as e:
        db.session.rollback()
        resp = jsonify({"error": str(e)})
        resp.status_code = 500
        return resp


@app.route('/runs/<int:run_id>', methods=['PUT'])
def update_run(runid):
    """Update the specified run"""
    run = db.session.query(Run).filter_by(runid=runid).first()
    if run is None:
        return not_found(runid)
    json_data = request.get_json()
    if not json_data:
        abort(400)
    data, errors = RunSchema().load(json_data, partial=True)
    if errors:
        return jsonify(errors), 400
    if 'effort' in data:
        run.effort = data['effort']
    if 'comment' in data:
        run.comment = data['comment']
    if 'rdate' in data:
        run.rdate = data['rdate']
    if 'timeofday' in data:
        run.timeofday = data['timeofday']
    if 'distance' in data:
        run.distance = data['distance']
    if 'units' in data:
        run.units = data['units']
    if 'elapsed' in data:
        run.elapsed = data['elapsed']
    db.session.add(run)
    db.session.commit()
    return (jsonify({'run': RunSchema().dump(run)}), 201,
            {'Location': url_for('get_run', run_id=runid,
                                 _external=True)})


@app.route('/runs', methods=['POST'])
def create_run():
    """Create a new run"""
    json_data = request.get_json()
    if not json_data:
        abort(400)
    # Validate the input and deserialize it from the json body
    data, errors = RunSchema().load(json_data, partial=True)
    if errors:
        print(json_data['elapsed'])
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
        units=data['units'],
        elapsed=data['elapsed'],
        effort=effort,
        comment=comment,
    )
    db.session.add(run)
    db.session.commit()
    return (jsonify({'run': RunSchema().dump(run)}), 201,
            {'Location': url_for('get_run', run_id=run.runid,
                                 _external=True)})


@app.route('/runs/latest')
def get_latest_run():
    """Get the most recent run"""
    run = db.session.query(Run).from_statement(
        text("SELECT * FROM runs r "
             "where r.rdate = (SELECT MAX(r2.rdate) FROM runs r2)")).first()
    if run is None:  # This is expected when there are no runs
        abort(404)
    return jsonify({'run': RunSchema().dump(run)})


@app.route('/runs/last/<int:days>')
def last_x_days(days):
    """Get all the runs in the past <int:days> days"""
    if days is None or days <= 0:
        return bad_request
    today = datetime.date.today()
    x_day = today + datetime.timedelta(0 - days)
    runs = Run.query.filter(cast(Run.rdate, DATE) >= x_day).all()
    # TODO return total miles and duration for the time period
    result = RunSchema().dump(runs, many=True)
    return jsonify({'runs': result.data})


@app.route('/stats/ytd')
def ytd():
    """Get statistics about runs since the first day of the current year"""
    jan1 = datetime.date(year=datetime.date.today().year, month=1, day=1)
    sql = text('select sum(r.distance*uc.factor) as distance from runs r, '
               'unit_conversion uc where uc.from_u = r.units and uc.to_u = '
               ' :units and r.distance is not null and r.rdate >= :date')
    results = db.engine.execute(sql, {'units': 'miles', 'date': jan1})
    result = results.first()[0]
    resp = {'distance': result,
            'units': 'miles'}
    return jsonify({'ytd': resp})


@app.route('/stats/yearly/ranges/<int:year>')
def yearly_stats(year):
    """Get statistics about runs in a given year
    This is provided as a list of distance ranges and the number of runs in
    each range."""
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
    return jsonify({'distance ranges': ranges})


@app.route('/help', methods=['GET'])
def help():
    """Print available endpoints"""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

if __name__ == '__main__':
    app.run(debug=True)
