from datetime import datetime

import pandas as pd
import pytest

import osmo_jupyter.calibration.do.prep as module


@pytest.fixture
def ysi_data_filepath(tmpdir):
    ysi_data_filepath = tmpdir / 'YSI_data.csv'
    pd.DataFrame([
        {
            'Timestamp': datetime(2019, 1, 1, 1, 1, 45),
            'Dissolved Oxygen (%)': 1,
            # Note: test_rounds_ysi_temperature_data expects this to not be an integer
            'Temperature (C)': 34.7,
            'irrelevant': 'other stuff'
        },
        {
            'Timestamp': datetime(2019, 1, 1, 1, 2, 11),
            'Dissolved Oxygen (%)': 1,
            'Temperature (C)': 34.7,
            'irrelevant': 'other stuff'
        },
    ]).to_csv(ysi_data_filepath)
    return ysi_data_filepath


@pytest.fixture
def image_data_filepath(tmpdir):
    image_data_filepath = tmpdir / 'roi_summary_data.csv'
    pd.DataFrame([
        {
            'timestamp': datetime(2019, 1, 1, 1, 1, 45),
            'ROI': 'DO patch',
            'r_msorm': 0.5,
            'irrelevant': 'other stuff'
        },
        {
            'timestamp': datetime(2019, 1, 1, 1, 1, 45),
            'ROI': 'Reference patch',
            'r_msorm': 0.1,
            'irrelevant': 'other stuff'
        },
        {
            'timestamp': datetime(2019, 1, 1, 1, 2, 11),
            'ROI': 'DO patch',
            'r_msorm': 0.6,
            'irrelevant': 'other stuff'
        },
        {
            'timestamp': datetime(2019, 1, 1, 1, 2, 11),
            'ROI': 'Reference patch',
            'r_msorm': 0.09,
            'irrelevant': 'other stuff'
        }
    ]).to_csv(image_data_filepath)
    return image_data_filepath


class TestPrepCalibrationData:

    def test_rounds_ysi_temperature_data(self, ysi_data_filepath, image_data_filepath):
        # Note: test assumes the YSI data fixture has non-integer temperatures. Otherwise the test does nothing.

        calibration_data = module.prep_calibration_data(
            ysi_data_filepath,
            image_data_filepath,
            'DO patch',
            'Reference patch',
        )

        assert not (calibration_data['Temperature (C)'] % 1).any()

    def test_combines_ysi_and_camera_data_appropriately(self, ysi_data_filepath, image_data_filepath):
        calibration_data = module.prep_calibration_data(
            ysi_data_filepath,
            image_data_filepath,
            'DO patch',
            'Reference patch',
        )

        expected_columns = [
            'timestamp',
            'Temperature (C)',
            'DO (% sat)',
            'DO patch reading',
            'Reference patch reading',
            'SR reading',
        ]

        expected_calibration_data = pd.DataFrame(
            [
                {
                    'timestamp': pd.Timestamp('2019-01-01 01:01:45'),
                    'Temperature (C)': 35.0,
                    'DO (% sat)': 1.0,
                    'DO patch reading': 0.5,
                    'Reference patch reading': 0.1,
                    'SR reading': 5.0
                },
                {
                    'timestamp': pd.Timestamp('2019-01-01 01:02:11'),
                    'Temperature (C)': 35.0,
                    'DO (% sat)': 1.0,
                    'DO patch reading': 0.6,
                    'Reference patch reading': 0.09,
                    'SR reading': 6.666666666666667
                }
            ],
            columns=expected_columns
        )

        pd.testing.assert_frame_equal(calibration_data, expected_calibration_data)
