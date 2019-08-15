import os
from typing import List

import numpy as np
import pandas as pd


def _interpolate_and_join_data(df_1: pd.DataFrame, df_2: pd.DataFrame) -> pd.DataFrame:
    # Upsample df_1 to every second to allow any timestamp to be joined on a strict match
    resampled_df_1 = df_1.resample("s").interpolate(method="slinear")

    return df_2.join(  # By default join happens on index values
        resampled_df_1, how="inner"  # Drop any rows without a match in both DataFrames
    )


def open_picolog_file(picolog_filepath):
    return (
        pd.read_csv(
            picolog_filepath,
            index_col=0,  # first column, is unlabeled
            parse_dates=[0],  # first column
            date_parser=lambda col: pd.to_datetime(col, utc=False).tz_localize(
                None
            ),  # Remove timezone information
        )
        .rename_axis("timestamp")
        .add_prefix("PicoLog ")
    )


def open_calibration_log_file(calibration_log_filepath):
    return pd.read_csv(
        calibration_log_filepath,
        index_col="timestamp",
        parse_dates=["timestamp"],
        date_parser=lambda col: pd.to_datetime(col, utc=False).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),  # Truncate fractional seconds
    )


def open_and_combine_picolog_and_calibration_data(
    calibration_log_filepaths: List[str], picolog_log_filepaths: List[str]
) -> pd.DataFrame:
    picolog_data = pd.concat(
        [
            open_picolog_file(picolog_filepath)
            for picolog_filepath in picolog_log_filepaths
        ],
        sort=True,
    )

    calibration_data = pd.concat(
        [
            open_calibration_log_file(calibration_log_filepath)
            for calibration_log_filepath in calibration_log_filepaths
        ],
        sort=True,
    )

    return _interpolate_and_join_data(picolog_data, calibration_data)


def get_equilibration_boundaries(equilibration_status: pd.Series) -> pd.DataFrame:
    # Get a boolean series with timestamped index of equilbrated data points
    equilibrated_mask = equilibration_status == "equilibrated"

    # Upsample to every second
    equilibration_status_sampler = equilibrated_mask.astype(int).resample("s")

    # In order to not interpolate any gaps around equilibrated states as also equilibrated, interpolate
    # state as an integer (True == 1) and truncate any decimals (e.g. 0.2 -> 0, or False)
    interpolated_equilbration_status = equilibration_status_sampler.interpolate().apply(
        np.floor
    )

    # rolling difference from previous row
    leading_edges = interpolated_equilbration_status[
        interpolated_equilbration_status.astype(int).diff() == 1
    ].index
    # rolling difference with next row
    trailing_edges = interpolated_equilbration_status[
        interpolated_equilbration_status.astype(int).diff(periods=-1) == 1
    ].index

    # Trim edges to align
    if len(leading_edges) > len(trailing_edges):
        leading_edges = leading_edges[:-1]
    if len(trailing_edges) > len(leading_edges):
        trailing_edges = trailing_edges[1:]

    return pd.DataFrame(
        {"leading_edge": leading_edges, "trailing_edge": trailing_edges}
    )


def pivot_process_experiment_results_on_ROI(
    experiment_df: pd.DataFrame,
    ROI_names: List[str] = None,
    msorm_types: List[str] = ["r_msorm", "g_msorm", "b_msorm"],
) -> pd.DataFrame:
    """
    Uses a pivot table to flatten multiple ROIs for the same image into one row.
    Returns a DataFrame with one row per image, and msorm values for a subset of ROIs.
    """
    if ROI_names:
        experiment_df = experiment_df[experiment_df["ROI"].isin(ROI_names)]

    # Pivot creates a heirachical multiindex data frame with an index for each 'values' column
    pivot = experiment_df.pivot(
        index="timestamp", columns="ROI", values=msorm_types + ["image"]
    )

    # There's one copy of the image name for each ROI due to the pivot, so pull out the top level index
    images = pivot["image"][experiment_df["ROI"].values[0]]
    pivot.drop("image", axis=1, inplace=True)
    # Flatten the pivot table index, and add images back in
    pivot.columns = [" ".join(col[::-1]).strip() for col in pivot.columns.values]
    pivot["image"] = images

    return pivot


def open_and_combine_process_experiment_results(
    results_filepaths: List[str],
    ROI_names: List[str] = None,
    msorm_types: List[str] = ["r_msorm", "g_msorm", "b_msorm"],
) -> pd.DataFrame:
    all_roi_data = pd.concat(
        [
            pd.read_csv(results_filepath, parse_dates=["timestamp"])
            for results_filepath in results_filepaths
        ]
    )

    return pivot_process_experiment_results_on_ROI(all_roi_data, ROI_names, msorm_types)


def get_all_experiment_images(
    local_sync_directory: str, experiment_names: List[str]
) -> pd.DataFrame:
    all_images = pd.concat(
        [
            pd.DataFrame(
                {
                    "experiment": experiment_name,
                    "image": os.listdir(
                        os.path.join(local_sync_directory, experiment_name)
                    ),
                },
                dtype="object",  # Ensure correct dtype when no images are found
            )
            for experiment_name in experiment_names
        ]
    )

    # Filter out experiment log files
    return all_images.drop(all_images[~all_images["image"].str.contains("jpeg")].index)


def filter_equilibrated_images(equilibration_range, image_ROI_data):
    leading_edge_mask = image_ROI_data.index > equilibration_range["leading_edge"]
    trailing_edge_mask = image_ROI_data.index < equilibration_range["trailing_edge"]
    return image_ROI_data[leading_edge_mask & trailing_edge_mask]


def open_and_combine_source_data(
    local_sync_directory: str,
    experiment_names: List[str],
    calibration_log_filepaths: List[str],
    picolog_log_filepaths: List[str],
    results_filepaths: List[str],
    ROI_names: List[str] = None,
    msorm_types: List[str] = ["r_msorm", "g_msorm", "b_msorm"],
) -> pd.DataFrame:

    all_sensor_data = open_and_combine_picolog_and_calibration_data(
        calibration_log_filepaths, picolog_log_filepaths
    )

    equilibration_boundaries = get_equilibration_boundaries(
        all_sensor_data["equilibration status"]
    )

    all_roi_data = open_and_combine_process_experiment_results(
        results_filepaths, ROI_names, msorm_types
    )

    equilibrated_data = pd.concat(
        equilibration_boundaries.apply(
            filter_equilibrated_images, axis=1, image_ROI_data=all_roi_data
        ).values
    ).sort_index()

    all_images = get_all_experiment_images(local_sync_directory, experiment_names)

    return (
        equilibrated_data.reset_index()
        .set_index("image")
        .join(all_images.set_index("image"), how="inner")
    )
