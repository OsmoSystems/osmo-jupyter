import datetime

import pandas as pd

from .parse import (
    TIMESTAMP,
    DO_PCT,
    DO_MGL,
    BAROMETRIC_PRESSURE_MMHG,
    TEMPERATURE_C,
    parse_calibration_log_file,
    parse_ysi_proodo_file,
    parse_ysi_prosolo_file,
)

_FILENAME_DATETIME_FORMAT = "%Y-%m-%d--%H-%M-%S"
FILENAME_TIMESTAMP_LENGTH = len("2018-01-01--12-01-01")

ATMOSPHERIC_OXYGEN_FRACTION = 0.2095  # From calibration-environment YSI driver

DATASET_COLUMNS = [
    TIMESTAMP,
    "YSI DO (mmHg)",
    f"YSI {DO_PCT}",
    f"YSI {DO_MGL}",
    f"YSI {BAROMETRIC_PRESSURE_MMHG}",
    f"YSI {TEMPERATURE_C}",
    "equilibration status",
    "setpoint O2 fraction",
    f"setpoint {TEMPERATURE_C}",
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


def _generate_time_based_setpoint_ids(dataset):
    """Create setpoint IDs that increment whenever there is a > 5 minute gap
    between image captures."""

    # this assumes the dataset is already sorted by timestamp, so let's assert that
    pd.testing.assert_frame_equal(dataset, dataset.sort_index())

    setpoint_transitions = dataset.index.to_series().diff() > datetime.timedelta(
        minutes=5
    )
    setpoint_ids = setpoint_transitions.astype(int).cumsum()
    return setpoint_ids


def _prepare_ysi_data(ysi_data: pd.DataFrame) -> pd.DataFrame:
    ysi_data["YSI DO (mmHg)"] = _calculate_partial_pressure(
        do_percent_saturation=ysi_data["YSI DO (%)"],
        barometric_pressure_mmhg=ysi_data["YSI barometric pressure (mmHg)"],
    )

    ysi_data_resampled = ysi_data.resample("s").interpolate(method="slinear")
    ysi_data_rounded = ysi_data_resampled.round(6)

    return _remove_unused_columns(ysi_data_rounded)


def process_ysi_proodo_file(filepath: str) -> pd.DataFrame:
    ysi_data = parse_ysi_proodo_file(filepath)
    return _prepare_ysi_data(ysi_data)


def process_ysi_prosolo_file(filepath: str) -> pd.DataFrame:
    ysi_kordss_data = parse_ysi_prosolo_file(filepath)
    return _prepare_ysi_data(ysi_kordss_data)


def process_calibration_log_file(filepath: str) -> pd.DataFrame:
    calibration_data = parse_calibration_log_file(filepath)

    trimmed_calibration_data = _remove_unused_columns(calibration_data)

    rounded_calibration_data = trimmed_calibration_data.round(
        {"setpoint temperature (C)": 3, "setpoint O2 fraction": 6}
    )

    rounded_calibration_data["setpoint ID"] = _generate_time_based_setpoint_ids(
        rounded_calibration_data
    )

    return rounded_calibration_data
