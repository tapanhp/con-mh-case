# -*- coding: utf-8 -*-

# MD Mar-2015 Note: This file should contain only functions that call from standard library, not from models
# or any of our library files

import binascii
import copy
import functools
import os
import re
import sys
from numbers import Number
from random import randint

import datetime

import environment
from ohm_lib.config import config
from functions.time_zone import convert_to_local, pacific_now

TEST_EMAIL_FILE = './tmp/email_test.txt'
TEST_SMS_FILE = './tmp/sms_text.txt'


def geocodeUsAddress(geocode_client, system1, verbose=False):
    lat = 0
    lon = 0

    fields = ['system_name', 'state', 'city', 'zip', 'address']
    for field in fields:
        if system1[field] == None:
            system1[field] = ''
        elif field != 'zip':
            system1[field] = system1[field] + ", "

    arrSystemInfo = {
        'With system name': system1['system_name'] + system1['address'] + system1['city'] + system1['state'] + "USA  " +
                            system1['zip'],
        'All info': system1['address'] + system1['city'] + system1['state'] + "USA  " + system1['zip'],
        'No zip': system1['address'] + system1['city'] + system1['state'] + "USA",
        'No address': system1['city'] + system1['state'] + "USA  " + system1['zip'],
        'No city or address': system1['state'] + "USA  " + system1['zip'],
        'No address or zip': system1['city'] + system1['state'] + "USA",
        'Zip only': "USA  " + system1['zip']
    }

    if verbose == True:
        print system1['point_id'], arrSystemInfo['With system name']

    arrResults = []
    for system_type in arrSystemInfo:
        try:
            arrResults = list(geocode_client.geocode(arrSystemInfo[system_type], exactly_one=False))
        except Exception as exception_error:
            dummy = 0

        for result in arrResults:
            geo_location, (lat, lon) = result

            if lat is None or lon is None or lat < 10 or lat > 150 or lon > -40 or lon < -200:
                lat, lon = 0, 0
            if lat > 0 and lon < 0:
                if verbose == True:
                    print geo_location, lat, lon, system_type, arrSystemInfo[system_type]
                return [geo_location.encode('utf-8'), lat, lon]

    # Not in US range
    return ['FAIL', 0, 0]


def levenshtein(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def find_best_match(model, arrOutputs):
    import difflib

    arrModels = []
    for model_entry in arrOutputs:
        arrModels.append(model_entry['info'])

    closest_matches = difflib.get_close_matches(model, arrModels)

    if len(closest_matches) > 0:
        return closest_matches[0]

    min_lev = len(model) * 3
    lev_info = ''
    for make_id in range(len(arrModels)):
        lev = levenshtein(model, arrModels[make_id]) / len(arrModels[make_id])
        if lev < min_lev:
            min_lev = lev
            lev_info = arrModels[make_id]
    if (min_lev / len(model)) < 0.5:
        return lev_info

    return -1

def google_places_api_qry(lat, lon, query_string, log, radius=None, max_attempts=5, testing=False):
    import urllib2, time, json

    apiKey = 'AIzaSyCmHxgeahVexFTQJNfeK3kUFuCyqEGyGw0'

    query_string = query_string.replace(" ", "+")
    if radius == None:
        url = '''https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&keyword=%s&sensor=false&rankby=distance&key=%s''' % (
            lat, lon, query_string, apiKey)
    else:
        url = '''https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&keyword=%s&sensor=false&radius=%s&key=%s''' % (
            lat, lon, query_string, radius, apiKey)

    if testing is True:
        print url
        exit()
    cnt_attempts = 0
    bln_success = 0
    while bln_success == 0 and cnt_attempts < min(max_attempts, 10):
        try:
            time.sleep(0.05 + cnt_attempts)
            station_scrape = urllib2.urlopen(url)
            bln_success = 1
        except:
            cnt_attempts += 1
            log.write("Google request failed once. Trying %s / %s times to fix issue" % (cnt_attempts, max_attempts))

    if bln_success == 0:
        return []

    station_json = station_scrape.read()
    arrStations = json.loads(station_json)
    return arrStations


def fuel_type_mapping(conn, tableName, fieldName, verbose=False):
    conn.execute('''SELECT name, fuel_type FROM gas.fuel_type ORDER BY order_evaluated''')
    arrFuels = conn.fetchall()
    cnt = 0
    for fuel in arrFuels:
        cnt += 1
        conn.execute('''UPDATE {0} SET fuel_type = '{2}' WHERE fuel_type = '' AND {1} LIKE '{3}'
            '''.format(tableName, fieldName, fuel['fuel_type'], "%" + fuel['name'] + "%"))
        if verbose == True and cnt % 10 == 5:
            print "Finished mapping a total of %s fuels (out of %s) for %s" % (cnt, len(arrFuels), tableName)
    return len(arrFuels)


def haversine(lon1, lat1, lon2, lat2):
    from math import radians, cos, sin, asin, sqrt

    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    mi = 6367 * c * 0.621371
    return mi


def wide_to_long(arrDict, idCols, num_values):
    import datetime

    arrLong = []
    interval = 24 * 60 / num_values
    for dict1 in arrDict:
        if dict1['dt'] == None:
            continue
        dttm = datetime.datetime.combine(dict1['dt'], datetime.time(0, 0))
        baseEntry = {}
        for col in idCols:
            baseEntry[col] = dict1[col]
        for i in range(1, num_values + 1):
            if i > 1:
                dttm = dttm + datetime.timedelta(minutes=interval)
            key_i = str(i)
            if i < 10 and dict1.has_key("value_%s" % i) == False and dict1.has_key("value_0%s" % i) == True:
                key_i = "0" + str(i)
            if dict1['value_%s' % key_i] == None:
                continue

            arrLong.append(dict(baseEntry.items() + {'dttm': dttm, 'value': dict1["value_%s" % key_i]}.items()))

    return arrLong


def page_query(q):
    offset = 0
    while True:
        r = False
        for elem in q.limit(1000).offset(offset):
            r = True
            yield elem
        offset += 1000
        if not r:
            break


def calc_short_name(name):
    if name is None:
        return '(None)'

    titleized_name = name.title()
    if titleized_name.find("@") > 0:
        titleized_name = titleized_name.split("@")[0]

    if len(titleized_name) > 15:
        return titleized_name[0:12] + '...'  # Take the first 12 characters plus three dots makes 15 characters
    else:
        return titleized_name


def safe_int(num_str, default_value=0):
    if num_str is None:
        return default_value

    try:
        num = int(num_str)
        return num
    except ValueError:
        pass

    try:
        num = int(float(num_str))
    except ValueError:
        num = default_value

    return num


def safe_float(num_str, default_value=0.0):
    if num_str is None:
        return default_value

    try:
        num = float(num_str)
    except ValueError:
        num = default_value
    return num


# MD Mar-2014 We need to be careful with "str". While this is useful for converting numbers and datetimes to
# strings that can be used with "replace", if it is a unicode string with non-ascii characters it will
# raise an exception. For example, "Meredith Özbil" causes problems because of the umlaut character.
def safe_str(field):
    if isinstance(field, basestring):
        return field
    else:
        return str(field)


def safe_strip(field):
    if isinstance(field, basestring):
        return field.strip()
    else:
        return field

def safe_strip_dict(d):
    for key, value in d.iteritems():
        d[key] = safe_strip(value)

    return d

def convert_deg_f_to_c(f):
    return (f - 32) * 5.0 / 9.0


def convert_deg_c_to_f(c):
    return c * 9.0 / 5.0 + 32

