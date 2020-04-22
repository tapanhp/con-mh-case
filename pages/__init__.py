
from flask.ext.login import current_user

import environment
from ohm_lib.config import config
from functions import app
from functions.ohm_strftime import format_date_pretty, format_date as ohm_format_date, \
    format_tm as ohm_format_tm, format_timezone_short as ohm_format_timezone_short


##################
# Custom Filters #
##################
@app.template_filter()
def pluralize(number, singular='', plural='s'):
    if number == 1:
        return singular

    return plural


@app.template_filter()
def pretty_date(dttm):
    return format_date_pretty(dttm)


@app.template_filter()
def format_date(dttm, iso=False, include_day_of_week=True):
    return ohm_format_date(dttm, iso, include_day_of_week)


@app.template_filter()
def format_tm(dttm):
    return ohm_format_tm(dttm)

@app.template_filter()
def format_timezone_short(dttm):
    return ohm_format_timezone_short(dttm)


@app.template_filter()
def local_dttm(dttm):
    if current_user.is_authenticated():
        local_dttm = current_user.local_dttm(dttm)
    else:
        local_dttm = dttm

    return local_dttm

@app.template_filter()
def max_length(str, length=5):

    if len(str) > length:
        text_length = length - 3  # add 3 for ...
        return str[:text_length] + "..."

    return str


@app.context_processor
def jinja_functions():

    return dict(
                config=config(),
                environment=environment,
                oem='ohm'
                )




