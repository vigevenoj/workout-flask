from app import db
from marshmallow import Schema, fields, validates, ValidationError


class Run(db.Model):
    __tablename__ = 'runs'
    runid = db.Column(db.Integer, db.Sequence('runs_runid_seq'),
                      primary_key=True)
    rdate = db.Column(db.Date())
    timeofday = db.Column(db.String())
    distance = db.Column(db.Numeric())
    units = db.Column(db.String())
    elapsed = db.Column(db.Interval())
    effort = db.Column(db.String(), nullable=True)
    comment = db.Column(db.String(), nullable=True)


class RunSchema(Schema):
    runid = fields.Int()
    rdate = fields.Date()
    timeofday = fields.Str()
    distance = fields.Decimal(as_string=True)
    units = fields.Str()
    elapsed = fields.TimeDelta()
    effort = fields.Str()
    comment = fields.Str()

    @validates('timeofday')
    def validate_timeofday(self, value):
        if value not in ['am', 'pm', 'noon']:
            raise ValidationError('Time of day not in range')

    @validates('units')
    def validate_units(self, value):
        if value not in ['m', 'km', 'miles']:
            raise ValidationError('Units must be one of m, km, or miles')
