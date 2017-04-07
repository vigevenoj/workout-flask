from app import db
from marshmallow import Schema, fields


class Run(db.Model):
    __tablename__ = 'runs'
    runid = db.Column(db.Integer, primary_key=True)
    rdate = db.Column(db.Date())
    timeofday = db.Column(db.String())
    distance = db.Column(db.Numeric())  # TODO numeric/decimal
    units = db.Column(db.String())
    elapsed = db.Column(db.Interval())  # TODO python probably has elapsed time?
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


class RunSchema(Schema):
    runid = fields.Int()
    rdate = fields.Date()
    timeofday = fields.Str()
    distance = fields.Decimal(as_string=True)
    units = fields.Str()
    elapsed = fields.TimeDelta()
    effort = fields.Str()
    comment = fields.Str()
