import pkg_resources

import pandas as pd
from unittest.mock import sentinel

import osmo_jupyter.dataset.parse as module


def test_parses_ysi_csv_correctly(tmpdir):
    test_ysi_classic_file_path = pkg_resources.resource_filename(
        "osmo_jupyter", "test_fixtures/test_ysi_classic.csv"
    )

    formatted_ysi_data = module.parse_ysi_proodo_file(test_ysi_classic_file_path)
    expected_ysi_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "YSI barometric pressure (mmHg)": 750,
                "YSI DO (% sat)": 19,
                "YSI temperature (C)": 24.7,
                "YSI unit ID": "unit ID",
            }
        ]
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(formatted_ysi_data, expected_ysi_data)


def test_parses_ysi_kordss_correctly(tmpdir):
    test_ysi_kordss_file_path = pkg_resources.resource_filename(
        "osmo_jupyter", "test_fixtures/test_ysi_kordss.csv"
    )

    formatted_ysi_data = module.parse_ysi_prosolo_file(test_ysi_kordss_file_path)
    expected_ysi_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "YSI barometric pressure (mmHg)": 750,
                "YSI DO (% sat)": 60,
                "YSI DO (mg/L)": 6,
                "YSI temperature (C)": 24.7,
            }
        ]
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(formatted_ysi_data, expected_ysi_data)


def test_parses_picolog_csv_correctly():
    test_picolog_file_path = pkg_resources.resource_filename(
        "osmo_jupyter", "test_fixtures/test_picolog.csv"
    )

    formatted_picolog_data = module.parse_picolog_file(test_picolog_file_path)
    expected_picolog_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "PicoLog temperature (C)": 39,
                "PicoLog barometric pressure (mmHg)": 750,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
                "PicoLog temperature (C)": 40,
                "PicoLog barometric pressure (mmHg)": 750,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:04"),
                "PicoLog temperature (C)": 40,
                "PicoLog barometric pressure (mmHg)": 750,
            },
        ]
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(formatted_picolog_data, expected_picolog_data)


def test_parses_calibration_log_correctly():
    test_calibration_log_file_path = pkg_resources.resource_filename(
        "osmo_jupyter", "test_fixtures/test_calibration_log.csv"
    )

    formatted_calibration_log_data = module.parse_calibration_log_file(
        test_calibration_log_file_path
    )
    # Nothing is supposed to be renamed or dropped, just datetime formatting
    expected_calibration_log_index = pd.DatetimeIndex(
        [
            pd.to_datetime("2019-01-01 00:00:00"),
            pd.to_datetime("2019-01-01 00:00:01"),
            pd.to_datetime("2019-01-01 00:00:03"),
            pd.to_datetime("2019-01-01 00:00:04"),
        ],
        name="timestamp",
    )

    pd.testing.assert_index_equal(
        formatted_calibration_log_data.index, expected_calibration_log_index
    )


class TestParseDataCollectionLog:
    def test_parses_data_collection_log_correctly(self):
        test_log_file_path = pkg_resources.resource_filename(
            "osmo_jupyter", "test_fixtures/test_data_collection_log.xlsx"
        )

        actual_data_collection_log = module.parse_data_collection_log(
            test_log_file_path
        )

        expected_data_collection_log = pd.DataFrame(
            [
                {
                    "experiment_names": [
                        "2019-07-26--19-34-38-Pi2E32-3000_images_attempt_1"
                    ],
                    "drive_directory": "2019-07-26 Collect 3000 images (attempt 1)",
                    "pond": "calibration",
                    "cosmobot_id": "A",
                    "cartridge_id": "C00003",
                    "start_date": pd.to_datetime("2019-07-26 19:12"),
                    "end_date": pd.to_datetime("2019-07-28 13:55"),
                },
                {
                    "experiment_names": [
                        "2019-08-26--23-34-10-PiE5FB-scum_tank_shakedown"
                    ],
                    "drive_directory": "2019-08-26 Scum Tank Shakedown",
                    "pond": "scum tank 1",
                    "cosmobot_id": "B",
                    "cartridge_id": "C00005",
                    "start_date": pd.to_datetime("2019-08-26 23:35"),
                    "end_date": pd.to_datetime("2019-08-27 08:15"),
                },
            ]
        )

        pd.testing.assert_frame_equal(
            actual_data_collection_log, expected_data_collection_log
        )

    def test_get_attempt_summary_gets_multiple_buckets(self):
        test_attempt_data = pd.Series(
            {
                "S3 Bucket(s)": "1\n2\n3",
                "Drive Directory": "Experiment",
                "Cosmobot ID": "Z",
                "Cartridge": "C1",
                "Start Date/Time": pd.to_datetime("2019"),
                "End Date/Time": pd.to_datetime("2020"),
            }
        )

        actual_attempt_summary = module._get_attempt_summary(test_attempt_data)

        expected_attempt_summary = pd.Series(
            {
                "experiment_names": ["1", "2", "3"],
                "drive_directory": "Experiment",
                "pond": "calibration",
                "cosmobot_id": "Z",
                "cartridge_id": "C1",
                "start_date": pd.to_datetime("2019"),
                "end_date": pd.to_datetime("2020"),
            }
        )

        pd.testing.assert_series_equal(actual_attempt_summary, expected_attempt_summary)


def test_interpolates_calibration_log_data_correctly(mocker):
    mock_calibration_log_data = pd.DataFrame(
        {
            "timestamp": [
                pd.to_datetime("2019-01-01 00:00:00"),
                pd.to_datetime("2019-01-01 00:00:02"),
            ],
            "YSI DO (mmHg)": [50, 30],
            "setpoint temperature (C)": [29.00000001, 30.0000003],
            "setpoint O2 fraction": [0.100000001, 0.3],
            "extraneous column": ["is", "dropped"],
        }
    ).set_index("timestamp")

    mocker.patch.object(
        module, "parse_calibration_log_file", return_value=mock_calibration_log_data
    )

    transformed_log_data = module.process_calibration_log_file(sentinel.log_file_name)

    expected_log_data = pd.DataFrame(
        {
            "timestamp": [
                pd.to_datetime("2019-01-01 00:00:00"),
                pd.to_datetime("2019-01-01 00:00:01"),
                pd.to_datetime("2019-01-01 00:00:02"),
            ],
            "YSI DO (mmHg)": [50, 40, 30],
            "setpoint temperature (C)": [29, 29.5, 30],
            "setpoint O2 fraction": [0.1, 0.2, 0.3],
        },
        dtype="float64",
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(
        transformed_log_data, expected_log_data, check_less_precise=6
    )


def test_setpoint_ids_assigned_correctly():
    mock_iamge_data = pd.DataFrame(
        {
            "timestamp": [
                # Each > than 5 minute jump should increment setpoint ID
                pd.to_datetime("2019-01-01 00:00:00"),
                pd.to_datetime("2019-01-01 00:05:00"),  # Don't increment
                pd.to_datetime("2019-01-01 00:10:01"),  # Increment
                pd.to_datetime("2019-01-01 00:16:00"),  # Increment
            ],
            "image": [
                sentinel.image1,
                sentinel.image2,
                sentinel.image3,
                sentinel.image4,
            ],
        }
    ).set_index("timestamp")

    setpoint_ids = module.generate_time_based_setpoint_ids(mock_iamge_data)

    expected_setpoint_ids = pd.Series([0, 0, 1, 2], index=mock_iamge_data.index).rename(
        "timestamp"
    )

    pd.testing.assert_series_equal(setpoint_ids, expected_setpoint_ids)


def test_prepare_ysi_data():
    # After the parse_* functions that two types of ysi data look mostly the same
    # so just test the common functionality here.
    # Only difference is ProSolo also includes mg/L values.
    mock_ysi_data = pd.DataFrame(
        {
            "timestamp": [
                pd.to_datetime("2019-01-01 00:00:00"),
                pd.to_datetime("2019-01-01 00:00:02"),
            ],
            "YSI DO (% sat)": [50, 51.000000001],
            "YSI DO (mg/L)": [3, 3.00003],
            "YSI temperature (C)": [29.00000001, 30],
            "YSI barometric pressure (mmHg)": [750, 755],
            "extraneous column": [0, 1],
        }
    ).set_index("timestamp")

    tranformed_ysi_data = module._prepare_ysi_data(mock_ysi_data)

    expected_ysi_data = pd.DataFrame(
        {
            "timestamp": [
                pd.to_datetime("2019-01-01 00:00:00"),
                # Interpolated value
                pd.to_datetime("2019-01-01 00:00:01"),
                pd.to_datetime("2019-01-01 00:00:02"),
            ],
            "YSI DO (% sat)": [50, 50.5, 51],
            "YSI DO (mg/L)": [3, 3.000015, 3.00003],
            "YSI temperature (C)": [29, 29.5, 30],
            "YSI barometric pressure (mmHg)": [750, 752.5, 755],
            # New column with derived-then-interpolated partial pressure values
            # Rounded to at most 6 sigfigs
            "YSI DO (mmHg)": [78.5625, 79.615238, 80.667975],
        }
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(
        tranformed_ysi_data, expected_ysi_data, check_less_precise=6
    )
