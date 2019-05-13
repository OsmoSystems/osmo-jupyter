from datetime import datetime

import pandas as pd
import pytest

from osmo_jupyter import ysi as module


ONE_MINUTE = datetime(2018, 1, 1, 12, 30, 0)

SINGLE_YSI_DATAPOINT = {'Timestamp': ONE_MINUTE, 'temperature': 20.0}
SINGLE_OTHER_DATAPOINT = {'timestamp': ONE_MINUTE, 'other': 5.0}


class TestGuardYsiIndexIsDatetime:
    def test_raises_if_index_is_not_datetime(self):
        with pytest.raises(ValueError):
            module._guard_ysi_data_index_is_datetime(pd.DataFrame([SINGLE_YSI_DATAPOINT]).set_index('temperature'))

    def test_does_not_raise_if_index_is_datetime(self):
        module._guard_ysi_data_index_is_datetime(pd.DataFrame([SINGLE_YSI_DATAPOINT]).set_index('Timestamp'))


class TestGuardOtherDataTimestampColumnIsDatetime:
    def test_raises_if_column_is_not_datetime(self):
        with pytest.raises(ValueError):
            module._guard_other_data_timestamp_column_is_datetime(
                other_data=pd.DataFrame([SINGLE_OTHER_DATAPOINT]),
                other_data_timestamp_column='other'
            )

    def test_does_not_raise_if_column_is_datetime(self):
        module._guard_other_data_timestamp_column_is_datetime(
            other_data=pd.DataFrame([SINGLE_OTHER_DATAPOINT]),
            other_data_timestamp_column='timestamp'
        )


class TestGuardNoFractionalSeconds:
    def test_raises_if_fractional_seconds(self):
        with pytest.raises(ValueError, match='other_data'):
            module._guard_no_fractional_seconds(
                datetime_series=pd.Series([
                    datetime(2018, 1, 1, 12, 30, 0),
                    datetime(2018, 1, 1, 12, 30, 1, microsecond=51),
                ]),
                series_name='other_data["timestamp"]'
            )

    def test_does_not_raise_if_whole_seconds(self):
        module._guard_no_fractional_seconds(
            datetime_series=pd.Series([
                datetime(2018, 1, 1, 12, 30, 0),
                datetime(2018, 1, 1, 12, 30, 1),
            ]),
            series_name="other_data['timestamp']"
        )


class TestJoinInterpolatedYsiData:
    def test_prefixes_with_YSI(self):
        actual = module.join_interpolated_ysi_data(
            other_data=pd.DataFrame([SINGLE_OTHER_DATAPOINT]),
            ysi_data=pd.DataFrame([SINGLE_YSI_DATAPOINT]).set_index('Timestamp')
        )

        assert 'YSI temperature' in list(actual.columns.values)

    def test_raises_if_YSI_index_not_datetime(self):
        with pytest.raises(ValueError):
            module.join_interpolated_ysi_data(
                other_data=pd.DataFrame([SINGLE_OTHER_DATAPOINT]),
                ysi_data=pd.DataFrame([SINGLE_YSI_DATAPOINT]).set_index('temperature')
            )

    def test_raises_if_other_data_timestamp_column_not_datetime(self):
        with pytest.raises(ValueError):
            module.join_interpolated_ysi_data(
                other_data=pd.DataFrame([SINGLE_OTHER_DATAPOINT]),
                ysi_data=pd.DataFrame([SINGLE_YSI_DATAPOINT]).set_index('Timestamp'),
                other_data_timestamp_column='other'
            )

    @pytest.mark.parametrize(
        'name,interpolation_method,other_seconds,ysi_seconds,expected_other_seconds,expected_ysi_seconds',
        [
            (
                'ysi seconds match other seconds',
                None,
                [3, 5, 7],
                [3, 5, 7],
                [3, 5, 7],
                [3, 5, 7]
            ),
            (
                'interpolates to match data with default (slinear) method',
                None,
                [3, 5, 7],
                [2, 4, 8],
                [3, 5, 7],
                [3, 5, 7],
            ),
            (
                'snaps to nearest second with "nearest" method',
                'nearest',
                [3, 5, 7],
                [2, 4, 8],
                [3, 5, 7],
                [2, 4, 8],
            ),
            (
                'discards extra YSI data',
                None,
                [3, 5, 7],
                [0, 2, 4, 6, 8],
                [3, 5, 7],
                [3, 5, 7]
            ),
            (
                'discards "other" data outside of ysi timerange',
                None,
                [3, 5, 7],
                [4, 5, 6],
                [5],
                [5]
            ),
        ]
    )
    def test_interpolates_to_nearest_second(
        self,
        name,
        interpolation_method,
        other_seconds,
        ysi_seconds,
        expected_other_seconds,
        expected_ysi_seconds
    ):
        # Only override the "interpolation_method" kwarg if provided
        method_kwargs = {} if interpolation_method is None else {'interpolation_method': interpolation_method}

        actual = module.join_interpolated_ysi_data(
            other_data=pd.DataFrame({
                'timestamp': [ONE_MINUTE.replace(second=s) for s in other_seconds],
                'other_data': other_seconds,
            }),
            ysi_data=pd.DataFrame({
                'Timestamp': [ONE_MINUTE.replace(second=s) for s in ysi_seconds],
                'ysi_data': ysi_seconds,
            }).set_index('Timestamp'),
            **method_kwargs
        )

        expected = pd.DataFrame({
            'timestamp': [ONE_MINUTE.replace(second=s) for s in expected_other_seconds],
            'other_data': expected_other_seconds,
            'YSI ysi_data': expected_ysi_seconds,
        })

        pd.testing.assert_frame_equal(
            actual,
            expected,
            check_like=True,  # Ignore column order
            check_dtype=False  # Allow different dtypes (int vs float)
        )

    def test_accepts_custom_timestamp_column_name(self):
        actual = module.join_interpolated_ysi_data(
            other_data=pd.DataFrame([{'custom_timestamp': ONE_MINUTE, 'other': 5.0}]),
            ysi_data=pd.DataFrame([{'Timestamp': ONE_MINUTE, 'temperature': 20.0}]).set_index('Timestamp'),
            other_data_timestamp_column='custom_timestamp'
        )

        expected = pd.DataFrame([{'custom_timestamp': ONE_MINUTE, 'other': 5.0, 'YSI temperature': 20.0}])

        pd.testing.assert_frame_equal(actual, expected, check_like=True)
