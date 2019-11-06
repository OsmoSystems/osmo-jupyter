from pathlib import Path

import pandas as pd

"""
In our Google Drive folder structure, each data collection event has a top-level folder. The structured data files
are all in a /data folder underneath that, organized in subfolders by data type.
The /data/setpoints folder will have all of the setpoints files, PicoLog files are under /data/pico, etc.

Note that based on the nature of the data collection, some data types may not be present in a particular folder. 

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


def _get_experiment_data_file_paths_for_type(project_directory, file_type):
    subdirectory_path = Path(project_directory) / DATA_DIRECTORY_NAME / file_type

    if not subdirectory_path.exists():
        return []

    files_in_subdirectory = sorted(
        filepath for filepath in subdirectory_path.iterdir() if filepath.is_file()
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
