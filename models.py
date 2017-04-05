from app import db


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
        return'<id {}>'.format(self.runid)
