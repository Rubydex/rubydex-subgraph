# coding=utf-8

import sys
import os
import time
import datetime
import functools
import collections
import calendar
import logging.handlers
import timeit
import copy
import stat
import pathlib
import json
import requests
from .logger import get_logger

logger = get_logger(__name__)

class DateTimeContants:
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR   = SECONDS_PER_MINUTE * 60
    SECONDS_PER_DAY    = SECONDS_PER_HOUR * 24
    SECONDS_PER_WEEK   = SECONDS_PER_DAY * 7


def get_now_datetime(tz=None):
    return datetime.datetime.now(tz)


def get_today_datetime():
    return datetime.datetime.today()


def get_yesterday_datetime():
    return datetime.datetime.today() - datetime.timedelta(days=1)


def get_datetime(year=None, month=None, day=None,
                 hour=0, minute=0, second=0, microsecond=0,
                 tzinfo=None):
    if year is None:
        year = 1

    if month is None:
        month = 1

    if day is None:
        day = 1

    if isinstance(tzinfo, str):
        tzinfo = get_timezone(tzinfo)

    return datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
        tzinfo=tzinfo,
    )


def get_all_timezones():
    import pytz
    return pytz.all_timezones


def get_timezone(timezone_name):
    import pytz
    return pytz.timezone(timezone_name)


def get_shanghai_timezone():
    return get_timezone('Asia/Shanghai')


def get_utc_timezone():
    return get_timezone('UTC')


def get_unix_timestamp_from_datetime(specified_datetime=None, is_microsecond_format=True):
    if not specified_datetime:
        specified_datetime = datetime.datetime.now()
    if isinstance(specified_datetime, str):
        specified_datetime = specified_datetime.replace('/', '-')
        specified_datetime = datetime.datetime.strptime(specified_datetime, "%Y-%m-%d")

    unix_timestamp = specified_datetime.timestamp()
    if is_microsecond_format:
        unix_timestamp = unix_timestamp * 1000000

    return int(unix_timestamp)


def get_datetime_from_unix_timestamp(unix_timestamp, is_utc=False, is_microsecond_format=True, timezone=None):
    if is_utc:
        if timezone is not None and timezone.zone != 'UTC':
            logger.error(f'''timezone({timezone.zone}) is not UTC, since is_utc is True''')
            return None
        result_datetime = datetime.datetime.utcfromtimestamp(unix_timestamp // 1000000 if is_microsecond_format else unix_timestamp)
    else:
        if isinstance(timezone, str):
            import pytz
            timezone = pytz.timezone(timezone)
        result_datetime = datetime.datetime.fromtimestamp(unix_timestamp // 1000000 if is_microsecond_format else unix_timestamp, tz=timezone)

    if is_microsecond_format:
        result_datetime = result_datetime.replace(microsecond=unix_timestamp % 1000000)

    return result_datetime


def get_unix_timestamp_seconds_from_datetime(specified_datetime=None):
    # TIMESTAMP FORMAT: "SECOND"
    timestamp_microseconds = get_unix_timestamp_from_datetime(specified_datetime=specified_datetime, is_microsecond_format=True)
    return int(timestamp_microseconds / 1000000)


def get_unix_timestamp_milliseconds_from_datetime(specified_datetime=None):
    # TIMESTAMP FORMAT: "MILLISECOND"
    timestamp_microseconds = get_unix_timestamp_from_datetime(specified_datetime=specified_datetime, is_microsecond_format=True)
    return int(timestamp_microseconds / 1000)


def get_unix_timestamp_microseconds_from_datetime(specified_datetime=None):
    # TIMESTAMP FORMAT: "MICROSECOND"
    timestamp_microseconds = get_unix_timestamp_from_datetime(specified_datetime=specified_datetime, is_microsecond_format=True)
    return int(timestamp_microseconds)


def get_unix_timestamp_seconds(year=None, month=None, day=None,
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=None):
    datetime_object = get_datetime(
        year, month, day,
        hour, minute, second, microsecond,
        tzinfo
    )

    return get_unix_timestamp_seconds_from_datetime(datetime_object)


def get_unix_timestamp_milliseconds(year=None, month=None, day=None,
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=None):
    datetime_object = get_datetime(
        year, month, day,
        hour, minute, second, microsecond,
        tzinfo
    )

    return get_unix_timestamp_milliseconds_from_datetime(datetime_object)


def get_unix_timestamp_microseconds(year=None, month=None, day=None,
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=None):
    datetime_object = get_datetime(
        year, month, day,
        hour, minute, second, microsecond,
        tzinfo
    )

    return get_unix_timestamp_microseconds_from_datetime(datetime_object)


def get_diff_days(start_date=None, end_date=None):
    if not start_date:
        start_date = datetime.datetime.today()
    if not end_date:
        end_date = datetime.datetime.today()
    if isinstance(start_date, str):
        start_date = start_date.replace('/', '-')
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = end_date.replace('/', '-')
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    return (end_date - start_date).days


def get_datetime_string(specified_datetime=None, string_format=None):
    if specified_datetime is None:
        specified_datetime = datetime.datetime.now()

    if string_format is None:
        string_format = '%Y-%m-%d %H:%M:%S'

    if isinstance(specified_datetime, str):
        specified_datetime = specified_datetime.replace('/', '-')
        specified_datetime = datetime.datetime.strptime(specified_datetime, "%Y-%m-%d")

    if not isinstance(specified_datetime, datetime.datetime):
        logger.error(f'specified_datetime is wrong type')
        return None

    if not isinstance(string_format, str):
        logger.error(f'specified_datetime is wrong type')
        return None

    return specified_datetime.strftime(string_format)


def get_datetime_from_string(specified_datetime_str, string_format=None, tzinfo='UTC'):
    if tzinfo == 'UTC':
        specified_datetime_str += ' +0000'
    if tzinfo == 'Asia/Shanghai':
        specified_datetime_str += ' +0800'

    if string_format is None:
        string_format = '%Y-%m-%d %H:%M:%S'

    if isinstance(specified_datetime_str, str):
        specified_datetime_str = specified_datetime_str.replace('/', '-')
        specified_datetime = datetime.datetime.strptime(specified_datetime_str, "%Y-%m-%d %H:%M:%S %z")
        return specified_datetime

    if not isinstance(specified_datetime_str, datetime.datetime):
        logger.error(f'specified_datetime is wrong type')
        return None

    if not isinstance(string_format, str):
        logger.error(f'specified_datetime is wrong type')
        return None

def get_specified_dates(start_date,
                        end_date,
                        include_start_date=True,
                        include_end_date=True,
                        return_type='date',
                        filter_none=False,
                        filter_first_day_by_month=False,
                        filter_last_day_by_month=False,
                        filter_monday_by_week=False):
    # region nested function
    def _get_first_day_by_month_dates(all_dates):
        first_day_by_month_dates = []
        for all_date in all_dates:
            if all_date.day == 1:
                first_day_by_month_dates.append(all_date)
        return first_day_by_month_dates

    def _get_last_day_by_month_dates(all_dates):
        last_day_by_month_dates = []
        for all_date in all_dates:
            _, month_range = calendar.monthrange(all_date.year, all_date.month)
            if all_date.day == month_range:
                last_day_by_month_dates.append(all_date)
        return last_day_by_month_dates

    def _get_monday_by_week_dates(all_dates):
        monday_by_week_dates = []
        for all_date in all_dates:
            if all_date.weekday() == 0:
                monday_by_week_dates.append(all_date)
        return monday_by_week_dates
    # endregion

    if not start_date:
        start_date = datetime.datetime.today()
    if not end_date:
        end_date = datetime.datetime.today()
    if isinstance(start_date, str):
        start_date = start_date.replace('/', '-')
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = end_date.replace('/', '-')
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    if not include_start_date:
        start_date = start_date + datetime.timedelta(days=1)
    if not include_end_date:
        end_date = end_date - datetime.timedelta(days=1)

    delta_days = (end_date - start_date).days
    if delta_days < 0:
        logger.error(f'start_date is greater than end_date: start_date({start_date}), end_date({end_date}), delta_days({delta_days})')
        return []

    all_dates = [(start_date + datetime.timedelta(days=i)) for i in range(0, delta_days+1)]

    specified_dates = []

    if filter_none:
        specified_dates += all_dates

    if filter_first_day_by_month:
        specified_dates += _get_first_day_by_month_dates(all_dates)

    if filter_last_day_by_month:
        specified_dates += _get_last_day_by_month_dates(all_dates)

    if filter_monday_by_week:
        specified_dates += _get_monday_by_week_dates(all_dates)

    specified_dates = list(set(specified_dates))
    specified_dates = sorted(specified_dates)
    if return_type.lower() == 'str':
        specified_dates = [f'''{specified_date.year:04}-{specified_date.month:02}-{specified_date.day:02}''' for specified_date in specified_dates]
    return specified_dates
