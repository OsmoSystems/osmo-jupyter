import datetime

import pytest
import pandas as pd

from osmo_jupyter import timezone as module


@pytest.mark.parametrize('input_datetime, expected_iso_output', [
    ('2018-01-01 12:00', '2018-01-01T12:00:00-08:00'),
    ('2018-06-01 12:00', '2018-06-01T12:00:00-07:00'),
])
def test_to_aware(input_datetime, expected_iso_output):
    output_datetime = module.to_aware(input_datetime)

    assert isinstance(output_datetime, datetime.datetime)
    assert output_datetime.isoformat() == expected_iso_output


def test_to_aware_blows_up_if_timezone_provided():
    time_string = '2018-01-01 12:00Z'
    with pytest.raises(ValueError):
        module.to_aware(time_string)


def test_to_utc_string():
    time_string = '2018-01-01 01:11'
    assert module.to_utc_string(time_string) == '2018-01-01 09:11:00'


def test_utc_series_to_local():
    utc_series = pd.Series(['2018-01-01 10:00', '2018-07-01 20:00'])
    expected_local_time_series = pd.to_datetime(pd.Series(['2018-01-01 18:00:00', '2018-07-02 03:00:00']))
    
    actual_local_time_series = module.utc_series_to_local(utc_series)

    pd.testing.assert_series_equal(actual_local_time_series, expected_local_time_series)
