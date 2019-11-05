import os
import pandas as pd

FILE_TYPES = [
    "setpoints",
    "calibration_log",
    "pico",
    "process_experiment",
    "ysi_proodo",
    "ysi_prosolo",
    "summary_movies",
]

DATA_DIRECTORY_NAME = "data"


def _get_experiment_data_file_paths_for_type(project_directory, file_type):
    subdirectory_path = os.path.join(project_directory, DATA_DIRECTORY_NAME, file_type)

    if not os.path.exists(subdirectory_path):
        return []

    files_and_folders_in_subdirectory = [
        os.path.join(subdirectory_path, filename)
        for filename in os.listdir(subdirectory_path)
    ]
    files_in_subdirectory = sorted(
        filepath
        for filepath in files_and_folders_in_subdirectory
        if os.path.isfile(filepath)
    )

    return files_in_subdirectory


def get_experiment_data_files_by_type(project_directory):
    """ Spider the provided directory for files related to an experiment.
    Expects the project directory to match our standard Google Drive experiment directory format.

    Args:
        project_directory: Google Drive experiment directory containing all of
            the data files for this data collection attempt
    Returns:
        pandas Series, indexed by file type and containing lists of filenames.
    """

    return pd.Series(
        {
            file_type: _get_experiment_data_file_paths_for_type(
                project_directory, file_type
            )
            for file_type in FILE_TYPES
        }
    )
