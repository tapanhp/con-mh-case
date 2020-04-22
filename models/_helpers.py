import json
import logging

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext import mutable
from sqlalchemy.sql import ClauseElement

from environment import DB_READ_ONLY
from functions import app


class OhmSQLAlchemy(SQLAlchemy):
    def safe_merge(self, record):
        if DB_READ_ONLY:
            return

        # MD Oct-2015 If a previous operation had an error and didn't rollback, the "begin" here will throw an
        # exception. In that case, rollback the previous one so we can continue with the current operation

        try:
            self.session.begin()
        except IntegrityError as e:
            db.session.rollback()
            db.session.begin()

            logging.error(e)

        try:
            self.session.merge(record)
            self.session.commit()
        except (DatabaseError, IntegrityError) as e:
            db.session.rollback()
            logging.error(e)

    def update_or_create(self, model, defaults={}, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            for k, v in defaults.iteritems():
                setattr(instance, k, v)
            self.session.flush()
        else:
            instance = self._add(model, defaults, **kwargs)

        return instance

    def get_or_create(self, model, defaults={}, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if not instance:
            instance = self._add(model, defaults, **kwargs)

        return instance

    def _add(self, model, defaults={}, **kwargs):
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        self.session.add(instance)
        self.session.flush()
        return instance


db = OhmSQLAlchemy(app, session_options={'autocommit': True, 'expire_on_commit': False})



class UTCDateTime(db.TypeDecorator):
    '''Results returned as aware datetimes, not naive ones.
    '''

    impl = db.DateTime

    def compare_values(self, x, y):
        return self.impl.compare_values(x, y)


class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        decoded_value = {}
        if value is not None:
            try:
                decoded_value = json.loads(value)
            except ValueError:
                pass

        return decoded_value


mutable.MutableDict.associate_with(JsonEncodedDict)
