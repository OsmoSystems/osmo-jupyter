from unittest.mock import sentinel

import pandas as pd

import osmo_jupyter.dataset.transform as module


def test_processes_log_data_correctly(mocker):
    mock_calibration_log_data = pd.DataFrame(
        {
            "timestamp": [
                pd.to_datetime("2019-01-01 00:00:00"),
                # One minute jump - shouldn't increase setpoint ID
                pd.to_datetime("2019-01-01 00:01:00"),
                # More than 5 minute jump - should increase setpoint ID
                pd.to_datetime("2019-01-01 00:07:00"),
            ],
            "YSI DO (mmHg)": [50, 40, 30],
            "setpoint temperature (C)": [29.111111111, 29.1, 30.0000003],
            "setpoint O2 fraction": [0.11111111111, 0.2222222222, 0.3],
            "extraneous column": ["should", "be", "dropped"],
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
                pd.to_datetime("2019-01-01 00:01:00"),
                pd.to_datetime("2019-01-01 00:07:00"),
            ],
            "YSI DO (mmHg)": [50, 40, 30],
            "setpoint temperature (C)": [29.111, 29.1, 30],
            "setpoint O2 fraction": [0.111111, 0.222222, 0.3],
            "setpoint ID": [0, 0, 1],
        }
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(transformed_log_data, expected_log_data)


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
            "YSI DO (%)": [50, 51.000000001],
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
            "YSI DO (%)": [50, 50.5, 51],
            "YSI DO (mg/L)": [3, 3.000015, 3.00003],
            "YSI temperature (C)": [29, 29.5, 30],
            "YSI barometric pressure (mmHg)": [750, 752.5, 755],
            # New column with derived-then-interpolated partial pressure values
            # Rounded to at most 6 sigfigs
            "YSI DO (mmHg)": [78.5625, 79.615238, 80.667975],
        }
    ).set_index("timestamp")

    pd.testing.assert_frame_equal(tranformed_ysi_data, expected_ysi_data)
