import pkg_resources
from unittest.mock import sentinel

import pandas as pd
import pytest

from . import spectrometer as module


class TestImportSpectrometerData:
    def test_import_spectrometer_txt(self):
        test_data_file_path = pkg_resources.resource_filename('osmo_jupyter', 'mock_spectrometer_data.txt')
        test_spectrometer_data = module._import_spectrometer_txt(test_data_file_path)
        mock_spectrometer_data = pd.DataFrame({
            'Unnamed: 0': ['2019-01-07 16:13:37.597000', '2019-01-07 16:13:42.397000', '2019-01-07 16:13:47.496000'],
            'Unnamed: 1': [1546906417597, 1546906422397, 1546906427496],
            '344.05': [-626.00, -640.67, -546.47],
            '1031.859': [627.00, 198.99, -546.47],
            '1032.175': [-163.15, -79.00, 189.10]
        })

        pd.testing.assert_frame_equal(mock_spectrometer_data, test_spectrometer_data)

    def test_broken_spectrometer_file(self):
        test_data_file_path = pkg_resources.resource_filename('osmo_jupyter', 'mock_bad_spectrometer_data.txt')

        with pytest.raises(ValueError):
            module._import_spectrometer_txt(test_data_file_path)


def test_clean_up_spectrometer_data_header():
    mock_unformatted_spectrometer_data = pd.DataFrame({
        'timestamp_with_wrong_name': [sentinel.timestamp],
        'epoch_time_with_wrong_name': [sentinel.epoch_timestamp],
        'wavelength_intensity': [sentinel.intensity]
    })

    expected_spectrometer_data_with_clean_header = pd.DataFrame({
        'timestamp': [sentinel.timestamp],
        'wavelength_intensity': [sentinel.intensity]
    })
    actual = module._clean_up_spectrometer_data_header(mock_unformatted_spectrometer_data)

    pd.testing.assert_frame_equal(actual, expected_spectrometer_data_with_clean_header)


def test_reformat_spectrometer_data():
    mock_unformatted_spectrometer_data = pd.DataFrame({
        'timestamp': ['2019-01-07 16:13:37.597000', '2019-01-07 16:13:42.397000', '2019-01-07 16:13:47.496000'],
        '344.05': [-626.00, -640.67, -546.47],
        '1031.859': [627.00, 198.99, -546.47],
        '1032.175': [-163.15, -79.00, 189.10]
    })
    actual = module._reformat_spectrometer_data(mock_unformatted_spectrometer_data)
    expected_formatted_spectrometer_data = pd.DataFrame({
        'timestamp': [
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000'
        ],
        'wavelength': [
            344.05,
            344.05,
            344.05,
            1031.859,
            1031.859,
            1031.859,
            1032.175,
            1032.175,
            1032.175,
        ],
        'intensity': [
            -626.00,
            -640.67,
            -546.47,
            627.00,
            198.99,
            -546.47,
            -163.15,
            -79.00,
            189.10,
        ],

    }).set_index('timestamp')
    pd.testing.assert_frame_equal(actual, expected_formatted_spectrometer_data)


def test_import_and_format_spectrometer_data():
    test_data_file_path = pkg_resources.resource_filename('osmo_jupyter', 'mock_spectrometer_data.txt')
    actual = module.import_and_format_spectrometer_data(test_data_file_path)
    expected_formatted_spectrometer_data = pd.DataFrame({
        'timestamp': [
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000'
        ],
        'wavelength': [
            344.05,
            344.05,
            344.05,
            1031.859,
            1031.859,
            1031.859,
            1032.175,
            1032.175,
            1032.175,
        ],
        'intensity': [
            -626.00,
            -640.67,
            -546.47,
            627.00,
            198.99,
            -546.47,
            -163.15,
            -79.00,
            189.10,
        ],

    }).set_index('timestamp')

    pd.testing.assert_frame_equal(actual, expected_formatted_spectrometer_data)


def test_spectrometer_intensity_summary():
    sample_formatted_spectrometer_data = pd.DataFrame({
        'timestamp': [
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000'
        ],
        'wavelength': [
            344.05,
            344.05,
            344.05,
            1031.859,
            1031.859,
            1031.859,
            1032.175,
            1032.175,
            1032.175,
        ],
        'intensity': [
            -626.00,
            -640.67,
            -546.47,
            627.00,
            198.99,
            -546.47,
            -163.15,
            -79.00,
            189.10,
        ],
    }).set_index('timestamp')

    actual = module.spectrometer_intensity_summary(
        sample_formatted_spectrometer_data,
        minimum_wavelength=344,
        maximum_wavelength=1032
    )
    expected_high_wavelength_intensity_summary = pd.DataFrame({
        'timestamp': [
            '2019-01-07 16:13:37.597000',
            '2019-01-07 16:13:42.397000',
            '2019-01-07 16:13:47.496000',
        ],
        'intensity': [
            0.5,
            -220.84,
            -546.47,
        ]
    }).set_index('timestamp')

    pd.testing.assert_frame_equal(actual, expected_high_wavelength_intensity_summary)
