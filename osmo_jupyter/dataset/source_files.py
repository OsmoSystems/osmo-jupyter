from pathlib import Path
from typing import List

import boto
import pandas as pd

EXPERIMENTS_BUCKET_NAME = "camera-sensor-experiments"


"""
In our Google Drive folder structure, each data collection event has a top-level folder. The structured data files
are all in a /data folder underneath that, organized in subfolders by data type.
The /data/setpoints folder will have all of the setpoints files, PicoLog files are under /data/pico, etc.

Note that based on the nature of a particular data collection event, some subfolders may not be present.

Example Google Drive folder:
/data/Google Drive/Technical/Experiments/2019-08-23 Sweeps Attempt 11/
├── 2019-08-23 README - Collect Sweeps Attempt 11.gddoc
└── data
    ├── calibration_log
    │   └── 2019-08-23--12-37-43_calibration.csv
    ├── pico
    │   └── 2019-08-23_attempt_11_pico.csv
    ├── process_experiment
    │   └── 2019-08-23--13-10-40-[...] - summary statistics (generated 2019-08-27--10-34-46).csv
    ├── setpoints
    │   └── 2019-08-16--14-32-14_two_sweeps_setpoints_1_with_extra.csv
    └── summary_movies
        └── 2019-08-23--13-10-40-Pi2E32-sweeps_attempt_11_1566589063 - equilibrated images summary.mp4

Official docs:
https://docs.google.com/document/d/1ri0LNyxWqtZ5g05T7o2pd_VQp3-ndKRVRT1TjiwnnZY/edit#heading=h.hx6dx98ojbtg
"""
DATA_DIRECTORY_NAME = "data"

FILE_TYPE_SUBFOLDERS = [
    "setpoints",
    "calibration_log",
    "pico",
    "process_experiment",
    "ysi_proodo",
    "ysi_prosolo",
    "summary_movies",
]

SOURCE_DATA_FILETYPES = [".csv", ".mp4", ".gif"]


def _is_data_filepath(filepath):
    return filepath.is_file() and filepath.suffix in SOURCE_DATA_FILETYPES


def _get_experiment_data_file_paths_for_type(project_directory, file_type):
    subdirectory_path = Path(project_directory) / DATA_DIRECTORY_NAME / file_type

    if not subdirectory_path.exists():
        return []

    files_in_subdirectory = sorted(
        filepath
        for filepath in subdirectory_path.iterdir()
        if _is_data_filepath(filepath)
    )

    return files_in_subdirectory


def get_experiment_data_files_by_type(project_directory):
    """ Spider the provided directory for files related to an experiment.
    Expects the project directory to match our standard Google Drive experiment directory format.

    Args:
        project_directory: Google Drive experiment directory containing all of
            the data files for this data collection attempt
    Returns:
        pandas Series, indexed by file type and containing lists of filenames as Path objects.
    """

    return pd.Series(
        {
            file_type: _get_experiment_data_file_paths_for_type(
                project_directory, file_type
            )
            for file_type in FILE_TYPE_SUBFOLDERS
        }
    )


def get_all_experiment_image_filenames(experiment_names: List[str]) -> pd.DataFrame:
    """
        Get a DataFrame of all image files across multiple experiment data directories.

        Args:
            experiment_names: A list of experiment directory names in the local sync directory.
        Returns:
            DataFrame of all requested experiment images with the following columns:
                * experiment_name
                * image_filename
    """
    all_images = pd.DataFrame(
        [
            {"experiment_name": experiment_name, "image_filename": image_filename}
            for experiment_name in experiment_names
            for image_filename in _get_experiment_filenames_from_s3(experiment_name)
            if image_filename.endswith(".jpeg")  # Filter out experiment log files
        ],
        # Ensure correct dtype and column names when no images are found
        columns=["experiment_name", "image_filename"],
        dtype="object",
    )

    return all_images


# COPY PASTA - from cosmobot-process-experiment@4701dc6 - osmo_camera.s3
def _get_experiment_filenames_from_s3(experiment_directory: str) -> List[str]:
    s3_prefix = f"{experiment_directory}/"
    all_keys = _list_experiment_s3_bucket_contents(s3_prefix)
    prefix_length = len(s3_prefix)
    filenames = [key[prefix_length:] for key in all_keys]
    return filenames


# COPY PASTA - modified from cosmobot-process-experiment@4701dc6 - osmo_camera.s3
# removed S3 credentials - must be present in the local env to work
def _list_experiment_s3_bucket_contents(directory_name: str = "",) -> List[str]:
    """ Get a list of all of the files in a logical directory off s3, within the camera sensor experiments bucket.
    Arguments:
        directory_name: prefix within our experiments bucket on s3, inclusive of trailing slash if you'd like the list
            of files within a "directory". Default is '' to get the top-level index of the bucket.
    Returns:
        list of key names under the prefix provided.
    """
    s3 = boto.connect_s3()

    bucket = s3.get_bucket(EXPERIMENTS_BUCKET_NAME)
    keys = bucket.list(directory_name, "/")

    return list([key.name for key in keys])
