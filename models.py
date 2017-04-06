from app import db
# import json
import simplejson as json
from datetime import date
from datetime import datetime
from datetime import timedelta


class RunJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        # Let the base class default method raise the TypeError
        elif isinstance(obj, timedelta):
            return (datetime.min + obj).time().isoformat()
            # return str(obj)
        return json.JSONEncoder.default(self, obj)


class Run(db.Model):
    __tablename__ = 'runs'
    runid = db.Column(db.Integer, primary_key=True)
    rdate = db.Column(db.Date())
    timeofday = db.Column(db.String())
    distance = db.Column(db.String())  # TODO numeric/decimal
    units = db.Column(db.String())
    elapsed = db.Column(db.String())  # TODO python probably has elapsed time?
    effort = db.Column(db.String())
    comment = db.Column(db.String())

    def __init__(self, rdate, timeofday, distance, units, elapsed, effort,
                 comment):
        self.rdate = rdate
        self.timeofday = timeofday
        self.distance = distance
        self.units = units
        self.elapsed = elapsed
        self.effort = effort
        self.comment = comment

    def __repr__(self):
        rundict = {'rdate': self.rdate,
                   'timeofday': self.timeofday,
                   'distance': self.distance,
                   'units': self.units,
                   'elapsed': self.elapsed,
                   'effort': self.effort,
                   'comment': self.comment}
        return json.dumps(rundict, cls=RunJsonEncoder)
