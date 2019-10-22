import pandas as pd


def create_mock_file_path(tmpdir, data, file_name):
    mock_file_path = tmpdir.join(file_name)
    data.to_csv(mock_file_path, index=False)

    return mock_file_path


TEST_YSI_CSV_DATA = pd.DataFrame(
    [
        {
            "Timestamp": "2019-01-01 00:00:00",
            "Barometer (mmHg)": 750,
            "Dissolved Oxygen (%)": 19,
            "Temperature (C)": 24.7,
            "Unit ID": "unit ID",
            "Comment": None,
            "Site": None,
            "Folder": None,
        }
    ]
)

TEST_YSI_KORDSS_DATA = pd.DataFrame(
    [
        {
            "DATE": "2019-01-01",
            "TIME": "00:00:00",
            "Barometer (mmHg)": 750,
            "ODO (% Sat)": 60,
            "ODO (mg/L)": 6,
            "Temp (°C)": 24.7,
            "SITE": None,
            "DATA ID": None,
            "ODO (% Local)": 60,
        }
    ]
)

TEST_PICOLOG_DATA = pd.DataFrame(
    [
        {
            "": "2019-01-01T00:00:00-07:00",
            "Temperature Ave. (C)": 39,
            "Pressure (Voltage) Ave. (nV)": 10,
        },
        {
            "": "2019-01-01T00:00:02-07:00",
            "Temperature Ave. (C)": 40,
            "Pressure (Voltage) Ave. (nV)": 10,
        },
        {
            "": "2019-01-01T00:00:04-07:00",
            "Temperature Ave. (C)": 40,
            "Pressure (Voltage) Ave. (nV)": 10,
        },
    ]
)

TEST_CALIBRATION_DATA = pd.DataFrame(
    [
        {
            "timestamp": "2019-01-01 00:00:00.1",
            "equilibration status": "waiting",
            "setpoint temperature": 40,
        },
        {
            "timestamp": "2019-01-01 00:00:01.1",
            "equilibration status": "equilibrated",
            "setpoint temperature": 40,
        },
        {
            "timestamp": "2019-01-01 00:00:03.1",
            "equilibration status": "equilibrated",
            "setpoint temperature": 40,
        },
        {
            "timestamp": "2019-01-01 00:00:04.1",
            "equilibration status": "waiting",
            "setpoint temperature": 40,
        },
    ]
)


TEST_PROCESS_EXPERIMENT_DATA = pd.DataFrame(
    [
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
            "image": "image-0.jpeg",
            "ROI": "ROI 0",
            "r_msorm": 0.5,
            "g_msorm": 0.4,
        },
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
            "image": "image-0.jpeg",
            "ROI": "ROI 1",
            "r_msorm": 0.4,
            "g_msorm": 0.5,
        },
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
            "image": "image-1.jpeg",
            "ROI": "ROI 0",
            "r_msorm": 0.3,
            "g_msorm": 0.6,
        },
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
            "image": "image-1.jpeg",
            "ROI": "ROI 1",
            "r_msorm": 0.6,
            "g_msorm": 0.3,
        },
    ]
)
