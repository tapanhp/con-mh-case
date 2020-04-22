from datetime import datetime

from functions.time_zone import convert_to_local, convert_to_utc, is_timezone_currently_in_dst


def format_weekday_full_name(dttm):
    return dttm.strftime('%A')


def format_dttm_file(dttm):
    return dttm.strftime('%Y-%m-%d_%H-%M-%S')


def format_dttm_with_utc_offset(dttm):
    return dttm.strftime('%Y-%m-%d %H:%M:%S%z')


def format_dttm_oasis(dttm):
    oasis_datetime_format = "%Y%m%dT%H:%M%z"
    pacific_dttm = convert_to_local(dttm)
    str = pacific_dttm.strftime(oasis_datetime_format)
    return str


def format_dttm_caiso(dttm):
    oasis_datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    utc_dttm = convert_to_utc(dttm)
    str = utc_dttm.strftime(oasis_datetime_format)
    return str


def format_dttm_pretty(dttm):
    return dttm.strftime("%-I:%M %p, %b %d")  # eg "7:17 PM, Nov 29"


def format_date_pretty(dttm):
    return dttm.strftime("%m/%d")


def format_tm_period(start_dttm, end_dttm, include_minutes=True, include_tz=False):
    if include_minutes:
        start_dttm_str = format(start_dttm, "%-I:%M%p")
        end_dttm_str = format(end_dttm, "%-I:%M%p")
        formatstr = "{0}-{1}"
    else:
        start_dttm_str = format(start_dttm, "%-I%p")
        end_dttm_str = format(end_dttm, "%-I%p")
        formatstr = "{0} - {1}"

    # If the AM/PM indicators are the same, take off the first one
    if start_dttm_str[-2:] == end_dttm_str[-2:]:
        start_dttm_str = start_dttm_str[:-2]

    tm_period = formatstr.format(start_dttm_str, end_dttm_str)

    if include_tz:
        tm_period = "%s %s" % (tm_period, format_timezone_short(start_dttm))

    return tm_period


def format_dttm_period(start_dttm, end_dttm, include_day_of_week=True, iso_date=False):
    date_str = format_date(start_dttm, include_day_of_week, iso_date)
    tm_period = format_tm_period(start_dttm, end_dttm)

    return "{0}, {1}".format(date_str, tm_period)


def format_date(dttm, include_day_of_week=True, iso_date=False):
    if iso_date:
        date_str = str(dttm.date())
    elif include_day_of_week:
        date_str = format(dttm, "%A, %b %-d")
    else:
        date_str = format(dttm, "%b %-d")

    return date_str


def format_tm(dttm):
    return format(dttm, "%-I%p")


def format_posixtime(uuid1, seconds=0):
    """Convert the uuid1 timestamp to a standard posix timestamp
    """
    assert uuid1.version == 1, ValueError('only applies to type 1')
    t = uuid1.time
    t = t - 0x01b21dd213814000
    t = t / 1e7
    t += seconds
    if is_timezone_currently_in_dst('America/Los_Angeles'):
        return datetime.fromtimestamp(t + (3600 * 7)).strftime("%Y-%m-%dT%H:%M:%S.015Z")
    return datetime.fromtimestamp(t + (3600 * 8)).strftime("%Y-%m-%dT%H:%M:%S.015Z")


def format_timezone_short(dttm):
    return dttm.tzname()


def format_timezone_long(dttm):
    return dttm.tzinfo.zone
