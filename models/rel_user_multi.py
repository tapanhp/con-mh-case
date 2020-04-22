from ._helpers import *

class RelUserMulti(db.Model):
    __tablename__ = 'rel_user_multi'
    rum_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    rel_lookup = db.Column(db.String(255))
    attribute = db.Column(db.String(255))
    create_transaction_id = db.Column(db.Integer)
    create_time = db.Column(UTCDateTime, server_default=db.func.current_timestamp())
