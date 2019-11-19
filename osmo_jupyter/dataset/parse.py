""" Functions to parse and clean source data files in a consistent way.
"""
import datetime
from typing import Dict

import pandas as pd


# Standard column names to align various data formats on
TIMESTAMP_LABEL = "timestamp"
TEMPERATURE_C_LABEL = "temperature (C)"
BAROMETRIC_PRESSURE_MMHG_LABEL = "barometric pressure (mmHg)"
DO_PCT_LABEL = "DO (%)"
DO_MGL_LABEL = "DO (mg/L)"
DO_MMHG_LABEL = "DO (mmHg)"

_FILENAME_DATETIME_FORMAT = "%Y-%m-%d--%H-%M-%S"
FILENAME_TIMESTAMP_LENGTH = len("2018-01-01--12-01-01")

ATMOSPHERIC_OXYGEN_FRACTION = 0.2095  # From calibration-environment YSI driver

DATASET_COLUMNS = [
    TIMESTAMP_LABEL,
    f"YSI {DO_MMHG_LABEL}",
    f"YSI {DO_PCT_LABEL}",
    f"YSI {DO_MGL_LABEL}",
    f"YSI {BAROMETRIC_PRESSURE_MMHG_LABEL}",
    f"YSI {TEMPERATURE_C_LABEL}",
    "setpoint O2 fraction",
    f"setpoint {TEMPERATURE_C_LABEL}",
    "setpoint ID",
]


# COPYPASTA from cosmobot_process_experiment.file_structure
def datetime_from_filename(filename: str) -> datetime.datetime:
    """ Recover a datetime that has been encoded into a filename, also returning the remainder of the filename
    Arguments:
        filename: filename to process. Should start with an ISO-ish datetime
            as produced by iso_datetime_for_filename()
    Returns:
        a datetime.datetime object matching the one that was encoded in the filename
    """

    return datetime.datetime.strptime(
        filename[:FILENAME_TIMESTAMP_LENGTH], _FILENAME_DATETIME_FORMAT
    )


def _calculate_partial_pressure(do_percent_saturation, barometric_pressure_mmhg):
    do_fraction_saturation = do_percent_saturation * 0.01
    return (
        do_fraction_saturation * ATMOSPHERIC_OXYGEN_FRACTION * barometric_pressure_mmhg
    )


def _remove_unused_columns(df):
    columns_to_drop = [
        column_name for column_name in df.columns if column_name not in DATASET_COLUMNS
    ]

    return df.drop(columns=columns_to_drop)


def generate_time_based_setpoint_ids(timestamped_series: pd.Series) -> pd.Series:
    """ Generate a series of setpoint IDs based on gaps between timestamps in provided Series.
        Used to identify setpoint change by measuring time gap between image captures.

        This is dependent upon equilibration between setpoints taking >5 mins and the time between
        consecutive image captures at a setpoint being <5 mins.

        Args:
            timestamped_series: A datetime-indexed series
        Returns:
            A series mapping a setpoint ID to each index in the input series.
    """

    timestamps_sorted = timestamped_series.sort_index()

    setpoint_transitions = timestamps_sorted.index.to_series().diff() > datetime.timedelta(
        minutes=5
    )
    setpoint_ids = setpoint_transitions.astype(int).cumsum()
    return setpoint_ids


def _apply_parser_configuration(
    dataset: pd.DataFrame, parse_config: Dict
) -> pd.DataFrame:
    return (
        dataset.drop(columns=parse_config["drop"])
        .rename(columns=parse_config["rename"])
        .set_index("timestamp")
        .add_prefix(parse_config["prefix"])
    )


def parse_ysi_prosolo_file(filepath: str) -> pd.DataFrame:
    """ Open and format a YSI KorDSS/ProSolo formatted csv file, with standardized datetime parsing
        and cleaned up columns.

        Args:
            filepath: Filepath to a YSI KorDSS csv file.
        Returns:
            Pandas DataFrame of the data, with DATE and TIME columns parsed together,
            and standardized column names.
    """
    parse_config = {
        "rename": {
            "DATE_TIME": TIMESTAMP_LABEL,
            "Barometer (mmHg)": BAROMETRIC_PRESSURE_MMHG_LABEL,
            "ODO (% Sat)": DO_PCT_LABEL,
            "ODO (mg/L)": DO_MGL_LABEL,
            "Temp (°C)": TEMPERATURE_C_LABEL,
        },
        "drop": ["SITE", "DATA ID", "ODO (% Local)"],
        "prefix": "YSI ",
    }
    raw_data = pd.read_csv(
        filepath, skiprows=5, encoding="latin-1", parse_dates=[["DATE", "TIME"]]
    )
    return _apply_parser_configuration(raw_data, parse_config)


def parse_ysi_proodo_file(filepath: str) -> pd.DataFrame:
    """ Open and format a YSI "classic"/ProODO csv file, with standardized datetime parsing
        and cleaned up columns.

        Args:
            filepath: Filepath to a YSI csv file.
        Returns:
            Pandas DataFrame of the data, with Timestamp column parsed as a datetime dtype,
            and standardized column names.
    """
    parse_config = {
        "rename": {
            "Timestamp": TIMESTAMP_LABEL,
            "Barometer (mmHg)": BAROMETRIC_PRESSURE_MMHG_LABEL,
            "Dissolved Oxygen (%)": DO_PCT_LABEL,
            "Temperature (C)": TEMPERATURE_C_LABEL,
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
            "Unnamed: 0": TIMESTAMP_LABEL,
            "Temperature Ave. (C)": TEMPERATURE_C_LABEL,
            "Pressure Ave. (mmHg)": BAROMETRIC_PRESSURE_MMHG_LABEL,
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


def _prepare_ysi_data(ysi_data: pd.DataFrame) -> pd.DataFrame:
    ysi_data[f"YSI {DO_MMHG_LABEL}"] = _calculate_partial_pressure(
        do_percent_saturation=ysi_data[f"YSI {DO_PCT_LABEL}"],
        barometric_pressure_mmhg=ysi_data[f"YSI {BAROMETRIC_PRESSURE_MMHG_LABEL}"],
    )

    ysi_data_resampled = ysi_data.resample("s").interpolate(method="slinear")
    ysi_data_rounded = ysi_data_resampled.round(6)

    return _remove_unused_columns(ysi_data_rounded)


def process_ysi_proodo_file(filepath: str) -> pd.DataFrame:
    """ Parse a YSI ProODO data csv as a DataFrame with only the columns necessary for deep learning.
        Numerical values are rounded.

        Args:
            filepath: Path to the source file.
        Returns:
            DataFrame with timestamp and rounded temperature, DO, and barometric pressure vaules.
    """
    ysi_proodo_data = parse_ysi_proodo_file(filepath)
    return _prepare_ysi_data(ysi_proodo_data)


def process_ysi_prosolo_file(filepath: str) -> pd.DataFrame:
    """ Parse a YSI ProSolo data csv as a DataFrame with only the columns necessary for deep learning.
        Numerical values are rounded.

        Args:
            filepath: Path to the source file.
        Returns:
            DataFrame with timestamp and rounded temperature, DO, and barometric pressure vaules.
    """
    ysi_prosolo_data = parse_ysi_prosolo_file(filepath)
    return _prepare_ysi_data(ysi_prosolo_data)


def process_calibration_log_file(filepath: str) -> pd.DataFrame:
    """ Parse a calibration log file as a DataFrame with only the columns necessary for deep learning.
        Numerical values are rounded and setpoint IDs are generated based on time.

        Args:
            filepath: Path to the source file.
        Returns:
            DataFrame with timestamp, YSI data, rounded setpoint values, and setpoint IDs.
    """
    calibration_data = parse_calibration_log_file(filepath)

    trimmed_calibration_data = _remove_unused_columns(calibration_data)

    calibration_data_resampled = trimmed_calibration_data.resample("s").interpolate(
        method="slinear"
    )

    rounded_calibration_data = calibration_data_resampled.round(
        {"setpoint temperature (C)": 3, "setpoint O2 fraction": 6}
    )

    return rounded_calibration_data
