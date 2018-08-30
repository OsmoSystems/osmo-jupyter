import datetime

import pytz
import pandas as pd


OSMO_HQ_TIMEZONE = pytz.timezone('US/Pacific')
SQL_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # Time format favored by mysql


def to_aware(local_time):
    """ get a timezone-aware object from local time string(s).

    Args:
        local_time: string of local time in any valid non-timezone-aware ISO format
            Time should be in Osmo HQ local time.
            eg. ('2012-01-01 12:00:00', '2012-01-01 12:00', '2012-01-01')
    Returns:
        timezone-aware datetime object
    """
    time = datetime.datetime.fromisoformat(local_time)
    return OSMO_HQ_TIMEZONE.localize(time)


def to_utc_string(local_time):
    ''' Convert a local time string to a string in UTC that can be passed to the database

    Args:
        local_time: string of local time in any valid non-timezone-aware ISO format
            Time should be in Osmo HQ local time.
            eg. ('2012-01-01 12:00:00', '2012-01-01 12:00', '2012-01-01')
    Returns:
        UTC time string that can be used, for instance, for database queries
    '''
    aware_datetime = to_aware(local_time)
    return aware_datetime.astimezone(pytz.utc).strftime(SQL_TIME_FORMAT)


def utc_series_to_local(pandas_timeseries):
    ''' Convert a Pandas series of UTC times to local time
    Useful for converting node data timestamps for use in local-time notebooks.

    Args:
        pandas_timeseries: pandas Series of timezone-naive datetimes or strings in UTC
    Returns:
        Pandas timeseries of timezone-naive datetimes corresponding to Osmo HQ local time
    '''
    definitely_a_timeseries = pd.to_datetime(pandas_timeseries)

    localized_timeseries = definitely_a_timeseries.dt.tz_localize(OSMO_HQ_TIMEZONE)
    return localized_timeseries.dt.tz_convert('UTC').dt.tz_localize(None)
