import os
from typing import List, Dict
from enum import Enum

import pandas as pd


# Standard column names to align various data formats on
TIMESTAMP = "timestamp"
TEMPERATURE_C = "temperature (C)"
BAROMETRIC_PRESSURE_MMHG = "barometric pressure (mmHg)"
DO_PCT = "DO (%)"
DO_MGL = "DO (mg/L)"


class DataFileType(Enum):
    UNKNOWN = 0
    YSI_CLASSIC = 1
    YSI_KORDSS = 2
    PICOLOG = 3
    CALIBRATION_LOG = 4


def _apply_parser_configuration(
    dataset: pd.DataFrame, parse_config: Dict
) -> pd.DataFrame:
    return (
        dataset.drop(parse_config["drop"], axis=1)
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


def open_and_combine_picolog_and_calibration_data(
    calibration_log_filepaths: List[str], picolog_log_filepaths: List[str]
) -> pd.DataFrame:
    """
        Open and join a collection of PicoLog and calibration environment data files.

        Args:
            calibration_log_filepaths: A list of filepaths to calibration environment csv data log files.
            picolog_log_filepaths: A list of filepaths to PicoLog csv data files.
        Returns:
            DataFrame of PicoLog data joined with matching calibration environment data.
            PicoLog data is upsampled to 1 second increments and linearly interpolated
    """
    picolog_data = pd.concat(
        [
            parse_picolog_file(picolog_filepath)
            .resample("s")
            .interpolate(method="slinear")
            for picolog_filepath in picolog_log_filepaths
        ],
        sort=True,
    )

    calibration_data = pd.concat(
        [
            parse_calibration_log_file(calibration_log_filepath)
            for calibration_log_filepath in calibration_log_filepaths
        ],
        sort=True,
    )

    return calibration_data.join(  # By default join happens on index values
        picolog_data, how="inner"  # Drop any rows without a match in both DataFrames
    )


def get_equilibration_boundaries(equilibration_status: pd.Series) -> pd.DataFrame:
    """
        Parse a list of timestamped equilibration statuses into a DataFrame of start
        and end times of equilibrated states. Assumes all time between unequilibrated
        and equilibrated input points are unequilibrated.

        Args:
            equilibration_status: A Series of equilibration status strings.
        Returns:
            DataFrame of start and end times of equilibrated states.
    """
    # Get a boolean series with timestamped index of equilbrated data points
    equilibrated_mask = equilibration_status == "equilibrated"
    leading_edges = equilibrated_mask[equilibrated_mask.astype(int).diff() == 1].index
    trailing_edges = equilibrated_mask[
        equilibrated_mask.astype(int).diff(periods=-1) == 1
    ].index

    # Correct single point ranges to have leading and falling edges
    if (
        len(trailing_edges)
        and len(leading_edges)
        and trailing_edges[0] < leading_edges[0]
    ):
        # Prepend a trailing edge at the start of the dataset as its own leading edge
        leading_edges = trailing_edges[:1].append(leading_edges)

    if len(trailing_edges) > len(leading_edges):
        # use the first trailing edge as its own leading edge
        leading_edges = leading_edges.append(trailing_edges[:1])
    if len(leading_edges) > len(trailing_edges):
        # use the final leading edge as its own trailing edge
        trailing_edges = trailing_edges.append(leading_edges[-1:])

    return pd.DataFrame({"start_time": leading_edges, "end_time": trailing_edges})


def pivot_process_experiment_results_on_ROI(
    experiment_df: pd.DataFrame,
    ROI_names: List[str] = None,
    msorm_types: List[str] = None,
) -> pd.DataFrame:
    """
        Flatten a DataFrame of process experiment results down to one row per image.

        Args:
            experiment_df: A DataFrame of process experiment summary statistics.
            ROI_names: Optional. A list of ROI names to select. Defaults to all ROIs present.
            msorm_types: Optional. A list of MSORM column names to select. Defaults to all RGB channel MSORMs.
        Returns:
            DataFrame with one row per image, and msorm values for a subset of ROIs. Creates one column
            for every unique ROI in the dataset. NaN values are used when an image is missing an ROI.
    """
    if msorm_types is None:
        msorm_types = ["r_msorm", "g_msorm", "b_msorm"]

    if ROI_names:
        experiment_df = experiment_df[experiment_df["ROI"].isin(ROI_names)]

    # Before pivot
    # image     ROI             r_msorm     timestamp
    #     1     DO patch             .4     2019-01-01
    #     1     Reference Patch      .5     2019-01-01

    # Pivot creates a heirachical multiindex data frame with an index for each 'values' column
    pivot = experiment_df.pivot(
        index="timestamp", columns="ROI", values=msorm_types + ["image"]
    )

    # After pivot -> Multi-level index
    #              DO Patch                 Reference Patch
    # timestamp    image     r_msorm...     image   r_msorm...
    # 2019-01-01       1          .4            1        .5

    # There's one copy of the image name for each ROI due to the pivot, so pull out the top level index
    images = pivot["image"][experiment_df["ROI"].values[0]]
    pivot.drop("image", axis=1, inplace=True)
    # Flatten the pivot table index, and add images back in
    pivot.columns = [
        # ("r_msorm", "some ROI name") -> "some ROI name r_msorm"
        " ".join(col[::-1]).strip()
        for col in pivot.columns.values
    ]
    pivot["image"] = images

    # After flattening
    # timestamp    image     DO Patch r_msorm   Reference Patch r_msorm...
    # 2019-01-01       1                   .4                        .5

    return pivot


def open_and_combine_process_experiment_results(
    process_experiment_result_filepaths: List[str],
    ROI_names: List[str] = None,
    msorm_types: List[str] = None,
) -> pd.DataFrame:
    """
        Open multiple process experiment result files and combine into a single DataFrame with one row per image.

        Args:
            process_experiment_result_filepaths: A list of filepaths to process experiment summary statistics files.
            ROI_names: Optional. A list of ROI names to select. Defaults to all ROIs present.
            msorm_types: Optional. A list of MSORM column names to select. Defaults to all RGB channel MSORMs.
        Returns:
            DataFrame of all summary statistics flattened to one row per image with all selected ROIs.
    """
    if msorm_types is None:
        msorm_types = ["r_msorm", "g_msorm", "b_msorm"]

    all_roi_data = pd.concat(
        [
            pd.read_csv(results_filepath, parse_dates=["timestamp"])
            for results_filepath in process_experiment_result_filepaths
        ]
    )

    return pivot_process_experiment_results_on_ROI(all_roi_data, ROI_names, msorm_types)


def get_all_experiment_images(
    local_sync_directory: str, experiment_names: List[str]
) -> pd.DataFrame:
    """
        Get a DataFrame of all image files across multiple experiment data directories.

        Args:
            local_sync_directory: The local data directory, usually ~/osmo/cosmobot-data-sets
            experiment_names: A list of experiment directory names in the local sync directory.
        Returns:
            DataFrame of all image file names and the corresponding experiment name.
    """
    all_images = pd.DataFrame(
        [
            {"experiment": experiment_name, "image": image}
            for experiment_name in experiment_names
            for image in os.listdir(os.path.join(local_sync_directory, experiment_name))
        ],
        # Ensure correct dtype and column names when no images are found
        columns=["experiment", "image"],
        dtype="object",
    )

    # Filter out experiment log files
    return all_images.drop(all_images[~all_images["image"].str.contains("jpeg")].index)


def filter_equilibrated_images(equilibration_range: pd.Series, df: pd.DataFrame):
    """
        Filter a datetime indexed DataFrame to a given equilibration range

        Args:
            equilibration_range: A Series with indexed start_time and end_time values
            df: A datetime indexed DataFrame
        Returns:
            A filtered df containing only values whose index is between the given start_time and end_tim.
    """
    leading_edge_mask = df.index > equilibration_range["start_time"]
    trailing_edge_mask = df.index < equilibration_range["end_time"]
    return df[leading_edge_mask & trailing_edge_mask]


def open_and_combine_and_filter_source_data(
    local_sync_directory: str,
    experiment_names: List[str],
    calibration_log_filepaths: List[str],
    picolog_log_filepaths: List[str],
    process_experiment_result_filepaths: List[str],
    ROI_names: List[str] = None,
    msorm_types: List[str] = None,
) -> pd.DataFrame:
    """
        Combine and filter a collection of calibration environment, PicoLog, process experiment and image data
        into a neat DataFrame of all images taken during periods of equilibrated temperature and dissolved oxygen.
        PicoLog and calibration sensor data are linearly interpolated to the second to line up with image timestamps.

        Args:
            local_sync_directory: The local data directory, usually ~/osmo/cosmobot-data-sets
            experiment_names: A list of experiment directory names in the local sync directory.
            calibration_log_filepaths: A list of filepaths to calibration environment csv data log files.
            picolog_log_filepaths: A list of filepaths to PicoLog csv data files.
            process_experiment_result_filepaths: A list of filepaths to process experiment summary statistics files.
            ROI_names: Optional. A list of ROI names to select. Defaults to all ROIs present.
            msorm_types: Optional. A list of MSORM column names to select. Defaults to all RGB channel MSORMs.

        Returns:
            DataFrame of image and sensor data collected during equilibrated states.
    """
    if msorm_types is None:
        msorm_types = ["r_msorm", "g_msorm", "b_msorm"]

    picolog_data = pd.concat(
        [
            parse_picolog_file(picolog_filepath)
            .resample("s")
            .interpolate(method="slinear")
            for picolog_filepath in picolog_log_filepaths
        ],
        sort=True,
    )

    calibration_data = pd.concat(
        [
            parse_calibration_log_file(calibration_log_filepath)
            for calibration_log_filepath in calibration_log_filepaths
        ],
        sort=True,
    )

    equilibration_boundaries = get_equilibration_boundaries(
        calibration_data["equilibration status"]
    )

    all_roi_data = open_and_combine_process_experiment_results(
        process_experiment_result_filepaths, ROI_names, msorm_types
    )

    all_roi_and_picolog_data = all_roi_data.join(picolog_data, how="inner")

    equilibrated_sensor_data = pd.concat(
        equilibration_boundaries.apply(
            filter_equilibrated_images, axis=1, df=all_roi_and_picolog_data
        ).values
    )

    equilibrated_data = equilibrated_sensor_data.join(
        calibration_data.resample("s").interpolate(method="slinear").dropna(axis=1),
        how="inner",
    ).sort_index()

    all_images = get_all_experiment_images(local_sync_directory, experiment_names)

    return (
        equilibrated_data.reset_index()
        .set_index("image")
        .join(all_images.set_index("image"), how="inner")
    )
