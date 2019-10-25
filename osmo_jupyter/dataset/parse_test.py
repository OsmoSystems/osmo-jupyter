import pkg_resources

import pandas as pd

import osmo_jupyter.dataset.parse as module


def test_parses_ysi_csv_correctly(tmpdir):
    test_ysi_classic_file_path = pkg_resources.resource_filename(
        "osmo_jupyter", "test_fixtures/test_ysi_classic.csv"
    )

    formatted_ysi_data = module.parse_ysi_classic_file(test_ysi_classic_file_path)
    expected_ysi_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "YSI barometric pressure (mmHg)": 750,
                "YSI DO (%)": 19,
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

    formatted_ysi_data = module.parse_ysi_kordss_file(test_ysi_kordss_file_path)
    expected_ysi_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "YSI barometric pressure (mmHg)": 750,
                "YSI DO (%)": 60,
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
                "start_date": pd.to_datetime("2019"),
                "end_date": pd.to_datetime("2020"),
            }
        )

        pd.testing.assert_series_equal(actual_attempt_summary, expected_attempt_summary)
