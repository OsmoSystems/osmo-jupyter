import pkg_resources
from unittest.mock import sentinel

import pandas as pd
import pytest

from . import spectrometer as module


FORMATTED_SPECTROMETER_DF = pd.DataFrame({
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


class TestImportSpectrometerData:
    def test_import_spectrometer_txt(self):
        test_data_file_path = pkg_resources.resource_filename('osmo_jupyter',
                                                              'test_fixtures/mock_spectrometer_data.txt'
                                                              )
        test_spectrometer_df = module._import_spectrometer_txt(test_data_file_path)
        mock_spectrometer_df = pd.DataFrame({
            'Unnamed: 0': ['2019-01-07 16:13:37.597000', '2019-01-07 16:13:42.397000', '2019-01-07 16:13:47.496000'],
            'Unnamed: 1': [1546906417597, 1546906422397, 1546906427496],
            '344.05': [-626.00, -640.67, -546.47],
            '1031.859': [627.00, 198.99, -546.47],
            '1032.175': [-163.15, -79.00, 189.10]
        })

        pd.testing.assert_frame_equal(mock_spectrometer_df, test_spectrometer_df)

    def test_broken_spectrometer_file(self):
        test_data_file_path = pkg_resources.resource_filename('osmo_jupyter',
                                                              'test_fixtures/mock_bad_spectrometer_data.txt'
                                                              )
        with pytest.raises(ValueError):
            module._import_spectrometer_txt(test_data_file_path)


def test_clean_up_spectrometer_df_header():
    mock_unformatted_spectrometer_df = pd.DataFrame({
        'timestamp_with_wrong_name': [sentinel.timestamp],
        'epoch_time_with_wrong_name': [sentinel.epoch_timestamp],
        'wavelength_intensity': [sentinel.intensity]
    })

    expected_spectrometer_df_with_clean_header = pd.DataFrame({
        'timestamp': [sentinel.timestamp],
        'wavelength_intensity': [sentinel.intensity]
    })
    actual = module._clean_up_spectrometer_df_header(mock_unformatted_spectrometer_df)

    pd.testing.assert_frame_equal(actual, expected_spectrometer_df_with_clean_header)


def test_reformat_spectrometer_df():
    mock_unformatted_spectrometer_df = pd.DataFrame({
        'timestamp': ['2019-01-07 16:13:37.597000', '2019-01-07 16:13:42.397000', '2019-01-07 16:13:47.496000'],
        '344.05': [-626.00, -640.67, -546.47],
        '1031.859': [627.00, 198.99, -546.47],
        '1032.175': [-163.15, -79.00, 189.10]
    })
    actual = module._reformat_spectrometer_df(mock_unformatted_spectrometer_df)
    pd.testing.assert_frame_equal(actual, FORMATTED_SPECTROMETER_DF)


def test_import_and_format_spectrometer_data():
    test_data_file_path = pkg_resources.resource_filename('osmo_jupyter',
                                                          'test_fixtures/mock_spectrometer_data.txt'
                                                          )
    actual = module.import_and_format_spectrometer_data(test_data_file_path)
    pd.testing.assert_frame_equal(actual, FORMATTED_SPECTROMETER_DF)


@pytest.mark.parametrize(
    "minimum_wavelength, maximum_wavelength, expected_intensity_summary",
    [(344, 1032, pd.DataFrame({
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
                                }).set_index('timestamp')),
     (None, 500, pd.DataFrame({
                               'timestamp': [
                                   '2019-01-07 16:13:37.597000',
                                   '2019-01-07 16:13:42.397000',
                                   '2019-01-07 16:13:47.496000',
                               ],
                               'intensity': [
                                   -626.0,
                                   -640.67,
                                   -546.47,
                               ]
                               }).set_index('timestamp')),
     (1032, None, pd.DataFrame({
                                'timestamp': [
                                    '2019-01-07 16:13:37.597000',
                                    '2019-01-07 16:13:42.397000',
                                    '2019-01-07 16:13:47.496000',
                                ],
                                'intensity': [
                                    -163.15,
                                    -79.0,
                                    189.1,
                                ]
                                }).set_index('timestamp')),
     (None, None, pd.DataFrame({
                                 'timestamp': [
                                     '2019-01-07 16:13:37.597000',
                                     '2019-01-07 16:13:42.397000',
                                     '2019-01-07 16:13:47.496000',
                                 ],
                                 'intensity': [
                                     -54.05,
                                     -173.56,
                                     -301.28,
                                     ]
                                 }).set_index('timestamp')),
     ]
)
def test_spectrometer_intensity_summary(minimum_wavelength, maximum_wavelength, expected_intensity_summary):
    actual = module.spectrometer_intensity_summary(
        FORMATTED_SPECTROMETER_DF,
        minimum_wavelength=minimum_wavelength,
        maximum_wavelength=maximum_wavelength
    )
    if minimum_wavelength is None:
        actual = module.spectrometer_intensity_summary(
            FORMATTED_SPECTROMETER_DF,
            maximum_wavelength=maximum_wavelength
        )
    if maximum_wavelength is None:
        actual = module.spectrometer_intensity_summary(
            FORMATTED_SPECTROMETER_DF,
            minimum_wavelength=minimum_wavelength
        )
    if maximum_wavelength is None and minimum_wavelength is None:
        actual = module.spectrometer_intensity_summary(
            FORMATTED_SPECTROMETER_DF,
        )

    pd.testing.assert_frame_equal(actual, expected_intensity_summary)
