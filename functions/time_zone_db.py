import datetime
import pytz
from mysql.connector.conversion import MySQLConverter

from functions.time_zone import is_naive, get_tz_from_name, parse_with_timezone

global_db_tz = pytz.utc


def check_is_datetime(value):
    return value is not None and type(value) == datetime.datetime


def convert_to_timezone(value, tz=None):
    if not check_is_datetime(value):
        return value

    if is_naive(value):
        value = pytz.utc.localize(value)

    if not tz:
        tz = pytz.utc
    elif type(tz) == str:
        tz = pytz.timezone(tz)

    return value.astimezone(tz)


def convert_to_dttm(attribute):
    # MD Apr-2015 All datetime rel_user attributes are stored in Pacific time. For continuity, continue to
    # do so no matter what timezone the database is in. However at a lower level, it will attempt to convert
    # to whatever timezone the database is in so to bypass that, convert to a naive datetime
    if check_is_datetime(attribute):
        dttm = convert_to_timezone(attribute, 'US/Pacific')
        attribute = dttm.replace(tzinfo=None)
    return attribute


def convert_from_dttm(attribute, rel_lookup):
    if attribute is not None and (rel_lookup[-3:].upper() in ('_DT', '_AT') or rel_lookup[-5:] == '_DTTM'):
        attribute = parse_with_timezone(attribute, 'US/Pacific', 'US/Pacific')

        if rel_lookup[-3:].upper() in ('_DT'):
            attribute = attribute.date()

    return attribute


def local_datetime_to_db_timestamp(value):
    '''
    MD Apr-2015
    This will take a Python datetime with timezone and convert to the database timezone so it will be stored correctly.

    If the value is None, a date or time type, just return that exact value since we can't convert

    All the Python datetimes we deal with should be timezone aware. However if one slips through,
    assume it is UTC since the AWS servers are running in UTC

    :param value: datetime in any timezone
    :return: datetime in UTC
    '''
    if not check_is_datetime(value):
        return value

    if is_naive(value):
        db_timestamp = pytz.utc.localize(value)
    else:
        db_timestamp = value.astimezone(global_db_tz)

    # MD Jun-2015 Strip off any microseconds and timezones otherwise MySQL will complain when in STRICT_TRANS_TABLES mode
    return db_timestamp.strftime("%Y-%m-%d %H:%M:%S")


def db_timestamp_to_pacific_datetime(value):
    '''
    MD Apr-2015
    This takes a db timestamp value and converts to a Python datetime in the Pacific timezone

    :param value: db timestamp in the db timezone
    :return: datetime in Pacific timezone
    '''
    if not check_is_datetime(value):
        return value

    value = global_db_tz.localize(value)
    tz = pytz.timezone('US/Pacific')
    return value.astimezone(tz)


class OhmMySQLConverter(MySQLConverter):
    def _DATETIME_to_python(self, value, dsc=None):
        """Connector/Python always returns naive datetime.datetime

        Connector/Python always returns naive timestamps since MySQL has
        no time zone support. Since Ohm needs non-naive, assume all datetimes in database are in UTC
        then convert to Pacific Time

        Returns datetime.datetime()
        """
        if not value:
            return value

        dttm = MySQLConverter._DATETIME_to_python(self, value)
        if not dttm:
            return dttm

        if is_naive(dttm):
            dttm = db_timestamp_to_pacific_datetime(dttm)
        return dttm

    def _TIMESTAMP_to_python(self, value, dsc=None):
        return self._DATETIME_to_python(value, dsc=None)

    # MD Sep-2015 These allows Freezegun fakedatetime and fakedate objects to be saved in the database
    def _fakedatetime_to_mysql(self, value):
        return self._datetime_to_mysql(value)

    def _fakedate_to_mysql(self, value):
        return self._date_to_mysql(value)

    def _datetime_to_mysql(self, value):
        if not is_naive(value):
            value = value.replace(microsecond=0).astimezone(global_db_tz or pytz.utc)

        return MySQLConverter._datetime_to_mysql(self, value)


