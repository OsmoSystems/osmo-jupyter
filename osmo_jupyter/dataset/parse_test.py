import pandas as pd
import pytest

import osmo_jupyter.dataset.parse as module
from osmo_jupyter.dataset.test_fixtures import (  # noqa: F401
    create_mock_file_path,
    TEST_YSI_CSV_DATA,
    TEST_YSI_KORDSS_DATA,
    TEST_PROCESS_EXPERIMENT_DATA,
    TEST_PICOLOG_DATA,
    TEST_CALIBRATION_DATA,
)


@pytest.fixture
def mock_picolog_file_path(tmpdir):
    return create_mock_file_path(tmpdir, TEST_PICOLOG_DATA, "test_pico_data.csv")


@pytest.fixture
def mock_calibration_file_path(tmpdir):
    return create_mock_file_path(
        tmpdir, TEST_CALIBRATION_DATA, "test_calibration_data.csv"
    )


def test_parses_ysi_csv_correctly(tmpdir):
    mock_YSI_csv_file_obj = create_mock_file_path(
        tmpdir, TEST_YSI_CSV_DATA, "test_ysi.csv"
    )

    formatted_ysi_data = module.parse_ysi_classic_file(mock_YSI_csv_file_obj)
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
    mock_YSI_KorDSS_file_path = tmpdir.join("test_kordss.csv")
    # Real KorDSS file has other contents in this header, but it adds up to 5 lines
    mock_YSI_KorDSS_file_path.write("\n\n\n\n\n")
    TEST_YSI_KORDSS_DATA.to_csv(
        mock_YSI_KorDSS_file_path, index=False, mode="a", encoding="latin-1"
    )

    formatted_ysi_data = module.parse_ysi_kordss_file(mock_YSI_KorDSS_file_path)
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


def test_parses_picolog_csv_correctly(mock_picolog_file_path):
    formatted_picolog_data = module.parse_picolog_file(mock_picolog_file_path)
    expected_picolog_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "PicoLog temperature (C)": 39,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
                "PicoLog temperature (C)": 40,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:04"),
                "PicoLog temperature (C)": 40,
            },
        ]
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(formatted_picolog_data, expected_picolog_data)


def test_parses_calibration_log_correctly(mock_calibration_file_path):
    formatted_calibration_log_data = module.parse_calibration_log_file(
        mock_calibration_file_path
    )
    # Nothing is supposed to be renamed or dropped, just datetime formatting
    expected_calibration_log_data = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                "equilibration status": "waiting",
                "setpoint temperature": 40,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:01"),
                "equilibration status": "equilibrated",
                "setpoint temperature": 40,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:03"),
                "equilibration status": "equilibrated",
                "setpoint temperature": 40,
            },
            {
                "timestamp": pd.to_datetime("2019-01-01 00:00:04"),
                "equilibration status": "waiting",
                "setpoint temperature": 40,
            },
        ]
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(
        formatted_calibration_log_data, expected_calibration_log_data
    )
