from typing import List

import pandas as pd

from .source_files import get_all_experiment_images
from .parse import parse_picolog_file, parse_calibration_log_file
from .transform import datetime_from_filename


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


def get_images_by_experiment(
    experiment_metadata: pd.Series, local_sync_directory
) -> pd.DataFrame:
    """ Get all image file names with associated experiment metadata.
    """
    experiment_names = experiment_metadata["experiment_names"]

    images_by_experiment = get_all_experiment_images(
        local_sync_directory, experiment_names
    )

    images_by_experiment["timestamp"] = images_by_experiment["image"].apply(
        datetime_from_filename
    )

    images_by_experiment["cartridge_id"] = experiment_metadata["cartridge_id"]
    images_by_experiment["cosmobot_id"] = experiment_metadata["cosmobot_id"]
    images_by_experiment["pond"] = experiment_metadata["pond"]

    return images_by_experiment.set_index("timestamp")
