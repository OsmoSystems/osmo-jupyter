from typing import Dict

import pandas as pd


# Standard column names to align various data formats on
TIMESTAMP = "timestamp"
TEMPERATURE_C = "temperature (C)"
BAROMETRIC_PRESSURE_MMHG = "barometric pressure (mmHg)"
DO_PCT = "DO (%)"
DO_MGL = "DO (mg/L)"


def _apply_parser_configuration(
    dataset: pd.DataFrame, parse_config: Dict
) -> pd.DataFrame:
    return (
        dataset.drop(columns=parse_config["drop"])
        .rename(columns=parse_config["rename"])
        .set_index("timestamp")
        .add_prefix(parse_config["prefix"])
    )


def parse_ysi_kordss_file(filepath: str) -> pd.DataFrame:
    """ Open and format a YSI KorDSS formatted csv file, with standardized datetime parsing
        and cleaned up columns.

        Args:
            filepath: Filepath to a YSI KorDSS csv file.
        Returns:
            Pandas DataFrame of the data, with DATE and TIME columns parsed together,
            and standardized column names.
    """
    parse_config = {
        "rename": {
            "DATE_TIME": TIMESTAMP,
            "Barometer (mmHg)": BAROMETRIC_PRESSURE_MMHG,
            "ODO (% Sat)": DO_PCT,
            "ODO (mg/L)": DO_MGL,
            "Temp (°C)": TEMPERATURE_C,
        },
        "drop": ["SITE", "DATA ID", "ODO (% Local)"],
        "prefix": "YSI ",
    }
    raw_data = pd.read_csv(
        filepath, skiprows=5, encoding="latin-1", parse_dates=[["DATE", "TIME"]]
    )
    return _apply_parser_configuration(raw_data, parse_config)


def parse_ysi_classic_file(filepath: str) -> pd.DataFrame:
    """ Open and format a YSI "classic" csv file, with standardized datetime parsing
        and cleaned up columns.

        Args:
            filepath: Filepath to a YSI csv file.
        Returns:
            Pandas DataFrame of the data, with Timestamp column parsed as a datetime dtype,
            and standardized column names.
    """
    parse_config = {
        "rename": {
            "Timestamp": TIMESTAMP,
            "Barometer (mmHg)": BAROMETRIC_PRESSURE_MMHG,
            "Dissolved Oxygen (%)": DO_PCT,
            "Temperature (C)": TEMPERATURE_C,
            "Unit ID": "unit ID",
        },
        "drop": ["Comment", "Site", "Folder"],
        "prefix": "YSI ",
    }

    raw_data = pd.read_csv(filepath, parse_dates=["Timestamp"])
    return _apply_parser_configuration(raw_data, parse_config)


def parse_picolog_file(filepath: str) -> pd.DataFrame:
    """ Open and format a PicoLog csv file, with standardized datetime parsing
        and cleaned up columns.

        Args:
            filepath: Filepath to a PicoLog csv file.
        Returns:
            Pandas DataFrame of the data, with the unlabeled timestamp column parsed
            as a datetime dtype with the timezone stripped, and standardized column names.
    """
    parse_config = {
        "rename": {
            "Unnamed: 0": TIMESTAMP,
            "Temperature Ave. (C)": TEMPERATURE_C,
            "Pressure Ave. (mmHg)": BAROMETRIC_PRESSURE_MMHG,
        },
        "drop": ["Pressure (Voltage) Ave. (nV)"],
        "prefix": "PicoLog ",
    }
    raw_data = pd.read_csv(
        filepath,
        parse_dates=[0],
        date_parser=lambda col: pd.to_datetime(col, utc=False).tz_localize(None),
    )

    return _apply_parser_configuration(raw_data, parse_config)


def parse_calibration_log_file(filepath: str) -> pd.DataFrame:
    """ Open and format a calibration log csv file, with standardized datetime parsing.

        Args:
            filepath: Filepath to a PicoLog csv file.
        Returns:
            Pandas DataFrame of the raw data, with timestamp column parsed
            as a datetime dtype with fractional seconds truncated.
    """
    parse_config = {"rename": {}, "drop": [], "prefix": ""}
    raw_data = pd.read_csv(
        filepath,
        parse_dates=["timestamp"],
        date_parser=lambda col: pd.to_datetime(col, utc=False).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),  # Truncate fractional seconds
    )

    return _apply_parser_configuration(raw_data, parse_config)


def _get_attempt_summary(attempt: pd.Series) -> pd.Series:
    experiment_names = attempt["S3 Bucket(s)"].split("\n")
    pond = attempt["Scum Tank"] if "Scum Tank" in attempt.index else "calibration"
    return pd.Series(
        {
            "experiment_names": experiment_names,
            "drive_directory": attempt["Drive Directory"],
            "pond": pond.lower(),
            "cosmobot_id": attempt["Cosmobot ID"],
            "cartridge_id": attempt["Cartridge"],
            "start_date": attempt["Start Date/Time"],
            "end_date": attempt["End Date/Time"],
        }
    )


def parse_data_collection_log(filepath: str) -> pd.DataFrame:
    """ Open and summarize a data collection log .xlsx file containing sheets named
        "Calibration Environment" and "Scum tank".

        Args:
            filepath: Filepath to a data collection log .xlsx file
        Returns:
            Pandas DataFrame with one row per attempt with select columns from the source data.
            Columns include:
                experiment_names: A list of S3 Bucket experiment names
                drive_directory: Google Drive folder name where collected sensor data lives
                pond: The environment data was collected in, e.g. calibration, scum tank 1
                cosmobot_id: Alpha identifier of the Cosmobot used in the experiment
                start_date: Starting timestamp of data collection
                end_date: Ending timestamp of data collection
    """
    calibration_log = pd.read_excel(
        filepath,
        "Calibration Environment",
        parse_dates=["Start Date/Time", "End Date/Time"],
    )
    scum_log = pd.read_excel(
        filepath, "Scum tank", parse_dates=["Start Date/Time", "End Date/Time"]
    )

    return (
        pd.concat(
            [
                calibration_log.apply(_get_attempt_summary, axis=1),
                scum_log.apply(_get_attempt_summary, axis=1),
            ]
        )
        .sort_values("start_date")
        .reset_index(drop=True)
    )
