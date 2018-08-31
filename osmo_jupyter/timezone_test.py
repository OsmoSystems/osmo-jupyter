import datetime

import pandas as pd

from osmo_jupyter import timezone as module


def test_utc_series_to_local():
    utc_series = pd.Series(['2018-01-01 18:00', '2018-07-05 02:00'])
    expected_local_time_series = pd.Series([
        datetime.datetime(2018, 1, 1, 10, 0, 0),
        datetime.datetime(2018, 7, 4, 19, 0, 0),
    ])

    actual_local_time_series = module.utc_series_to_local(utc_series)

    pd.testing.assert_series_equal(actual_local_time_series, expected_local_time_series)
