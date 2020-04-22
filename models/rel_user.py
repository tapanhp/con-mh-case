from ._helpers import *
from sqlalchemy.orm import relationship

class RelUser(db.Model):
    __tablename__ = 'rel_user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    rel_lookup = db.Column(db.String(128), primary_key=True)
    attribute = db.Column(db.String(255))
    create_transaction_id = db.Column(db.Integer)
    create_time = db.Column(UTCDateTime, server_default=db.func.current_timestamp())
    user = relationship("User")


    @classmethod
    def find_all_by_rel_lookup(cls, rel_lookup):
        return RelUser.query.filter_by(rel_lookup=rel_lookup).all()

    @classmethod
    def find_by_lookup_attribute(cls, rel_lookup, attribute):
        return RelUser.query.filter_by(rel_lookup=rel_lookup, attribute=attribute).first()

