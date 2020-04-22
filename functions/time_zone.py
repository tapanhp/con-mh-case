import datetime
import pytz
from dateutil.parser import parse
from tzlocal import get_localzone


def tz_string(dttm):
    return dttm.tzname()  # eg 'PST' or 'PDT'

def get_tz_from_name(tz_or_name):
    if tz_or_name is None:
        tz = pytz.utc
    elif not isinstance(tz_or_name, basestring):
        tz = tz_or_name
    elif tz_or_name.upper() == 'SYSTEM':
        tz = get_localzone()
    elif ':' in tz_or_name:
        fields = tz_or_name.split(':')
        offset = int(fields[0]) * 60
        tz = pytz.FixedOffset(offset)
    else:
        tz = pytz.timezone(tz_or_name)
    return tz


def convert_to_local(dttm, tz_from=None, tz_to=None):
    if is_naive(dttm):
        tz_from = get_tz_from_name(tz_from)
        from_dttm = tz_from.localize(dttm)
    else:
        from_dttm = dttm

    if tz_to is None:
        tz_to = 'US/Pacific'
    tz_to = get_tz_from_name(tz_to)

    local_dttm = from_dttm.astimezone(tz_to)
    return local_dttm


def convert_to_utc(dttm):
    return convert_to_local(dttm, 'US/Pacific', "UTC")


def naive_utc_to_local(dttm, tz_name=None):
    return convert_to_local(dttm, tz_from=pytz.utc, tz_to=tz_name)


def epoch_to_local(epoch_seconds, tz_to=None):
    return naive_utc_to_local(datetime.datetime.utcfromtimestamp(epoch_seconds), tz_name=tz_to)

def as_local(dttm, tz_name):
    ptz = pytz.timezone(tz_name)
    return dttm.astimezone(ptz)

def local_now(tz_name):
    now = datetime.datetime.now()
    local_tz = get_localzone()
    local_dttm = local_tz.localize(now)
    return as_local(local_dttm, tz_name)

def pacific_now():
    return local_now('US/Pacific')

def pacific_now_delta(**kwargs):
    return pacific_now() + datetime.timedelta(**kwargs)

def pacific_start_of_day():
    return pacific_now().replace(hour=0, minute=0, second=0, microsecond=0)

def pacific_today():
    return pacific_now().date()

def pacific_today_delta(**kwargs):
    return pacific_today() + datetime.timedelta(**kwargs)


def utc_now():
    return local_now('UTC')


def parse_with_timezone(str_dttm, tz_from, tz_to):
    dttm = parse(str_dttm)
    return convert_to_local(dttm, tz_from, tz_to)


def parse_pacific(str_dttm):
    return parse_with_timezone(str_dttm, 'US/Pacific', 'US/Pacific')


def parse_utc_to_pacific(str_dttm):
    return parse_with_timezone(str_dttm, 'UTC', 'US/Pacific')

def parse_pacific_to_utc(str_dttm):
    return parse_with_timezone(str_dttm, 'US/Pacific', 'UTC')


def is_naive(value):
    """
    Determines if a given datetime.datetime is naive.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is None or value.tzinfo.utcoffset(value) is None

def is_timezone_currently_in_dst(time_zone):
    return bool(datetime.datetime.now(pytz.timezone(time_zone)).dst())

def is_date_in_dst(dttm):
    return bool(pytz.timezone('US/Pacific').dst(dttm, is_dst=None))

def pacific_today_with_offset():
    if is_timezone_currently_in_dst('America/Los_Angeles'):
        return '%sT00:00:00.000-07:00' % pacific_today()
    else:
        return '%sT00:00:00.000-08:00' % pacific_today()

def pacific_date_with_offset(str_dttm):
    d = datetime.datetime.strptime(str_dttm, "%Y-%m-%d")
    if is_date_in_dst(d):
        return '%sT00:00:00.000-07:00' % str_dttm
    else:
        return '%sT00:00:00.000-08:00' % str_dttm

def get_related_timezone(timezone, filter_by_common_name=False):
    related = {
        'US/Alaska': ['America/Anchorage', 'America/Nome', 'America/Yakutat', 'America/Juneau'],
        'Canada/Atlantic': ['America/Halifax', 'America/Puerto_Rico', 'Canada/Newfoundland'],
        'US/Arizona': ['America/Phoenix'],
        'US/Central': ['America/Chicago', 'Canada/Central', 'America/Indiana/Tell_City', 'Canada/Saskatchewan', 'America/Menominee',
                       'America/North_Dakota/Center', 'America/Indiana/Knox'],
        'US/Eastern': ['America/New_York', 'Canada/Eastern', 'America/Indiana/Vincennes', 'America/Detroit', 'America/Indiana/Marengo',
                       'America/Indiana/Winamac', 'America/Indiana/Indianapolis', 'America/Indiana/Vevay', 'America/Kentucky/Monticello',
                       'America/Kentucky/Louisville', 'America/Indiana/Petersburg'],
        'US/Hawaii': ['Pacific/Honolulu'],
        'US/Mountain': ['America/Denver', 'Canada/Mountain', 'America/Boise', 'America/Shiprock'],
        'US/Pacific': ['America/Los_Angeles', 'Canada/Pacific', 'Canada/Yukon'],
        'US/Pacific-New': ['America/Los_Angeles', 'Canada/Pacific', 'Canada/Yukon']
    }

    # If timezone = "America/Los_Angeles", return "US/Pacific"
    if filter_by_common_name:
        filtered = filter(lambda key: timezone in related[key], related.keys())
        return filtered[0] if filtered else None

    # If timezone = "US/Pacific", return ['America/Los_Angeles', 'Canada/Pacific', 'Canada/Yukon']
    return related.get(timezone)

def offset_to_timezone(offset, dst):
    gb_tz = {
        ('-18000', '3600') : 'America/New_York',  # -5
        ('-21600', '3600'): 'America/Chicago',    # -6
        ('-25200', '3600'): 'America/Denver',     # -7
        ('-25200', '0'): 'America/Phoenix',    # -7 no DST
        ('-28800', '3600'): 'America/Los_Angeles',
        ('-32400', '3600'): 'America/Anchorage',
        }
    tz_str = gb_tz.get((str(offset), str(dst)))
    if not tz_str:
        tz_str = 'America/Los_Angeles'
    return tz_str


def dstrule_to_dict(dstrule):
    """https://github.com/energyos/OpenESPI-Common-java/blob/master/etc/espiDerived.xsd
       Search for DstRuleType
    """
    if len(dstrule) != 8:
        return None

    br = bin(int(dstrule, 16))[2:].zfill(32)[::-1]
    d = {
        "Seconds": int(br[0:12][::-1], 2),
        "Hours": int(br[12:17][::-1], 2),
        "Day_of_Week": int(br[17:20][::-1], 2),  #  0=N/A,Mon=1
        "Day_of_Month": int(br[20:25][::-1], 2),  #  0=N/A
        "Operator": int(br[25:28][::-1], 2),
        "Month": int(br[28:32][::-1], 2)
    }
    return d

