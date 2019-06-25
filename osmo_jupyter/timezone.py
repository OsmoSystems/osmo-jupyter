import pytz
import pandas as pd


OSMO_HQ_TIMEZONE = pytz.timezone("US/Pacific")


def utc_series_to_local(pandas_timeseries):
    """ Convert a Pandas series of UTC times to local time
    Useful for converting node data timestamps for use in local-time notebooks.

    eg.
    >>> raw_node_data = osmo_jupyter.db_access.load_calculation_details(...)
    >>> raw_node_data['create_date'] = utc_series_to_local(raw_node_data['create_date'])

    Args:
        pandas_timeseries: pandas Series of timezone-naive datetimes or strings in UTC
    Returns:
        Pandas timeseries of timezone-naive datetimes corresponding to Osmo HQ local time
    """
    # Input may have been a series of strings or a series of datetimes
    definitely_a_timeseries = pd.to_datetime(pandas_timeseries)

    localized_timeseries = definitely_a_timeseries.dt.tz_localize("UTC")
    return localized_timeseries.dt.tz_convert(OSMO_HQ_TIMEZONE).dt.tz_localize(None)
