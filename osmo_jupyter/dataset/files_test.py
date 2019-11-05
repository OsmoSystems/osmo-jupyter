import os
import pandas as pd

import osmo_jupyter.dataset.files as module


def _init_data_dir(parent_dir, directories_to_include, files_to_include):
    """set up a data directory with folders and files in it
    Args:
        directories_to_include: iterable of directory names to initialize
        files_to_include: iterable of file names to initialize. If they are in subdirectories,
            the subdirectories should be listed in directories_to_include to be created first
    """
    data_dir = os.path.join(parent_dir, "data")
    os.mkdir(data_dir)

    for relative_directory_path in directories_to_include:
        os.makedirs(os.path.join(data_dir, relative_directory_path))

    for relative_file_path in files_to_include:
        with open(os.path.join(data_dir, relative_file_path), "w"):
            # Just opening the file is enough to create it.
            pass


class TestGetExperimentDataFilePathsForType:
    def test_no_directory_returns_empty(self, tmp_path):
        actual = module._get_experiment_data_file_paths_for_type(
            tmp_path, "this does NOT exist as a subdirectory"
        )
        expected = []
        assert actual == expected

    def test_gets_file_from_subdirectory_and_ignores_sub_subdirectories(self, tmp_path):
        _init_data_dir(
            tmp_path,
            directories_to_include=["ysi_proodo/subdirectory"],
            files_to_include=["ysi_proodo/somethin"],
        )
        actual = module._get_experiment_data_file_paths_for_type(tmp_path, "ysi_proodo")
        expected = [os.path.join(tmp_path, "data/ysi_proodo/somethin")]
        assert actual == expected

    def test_gets_multiple_files(self, tmp_path):
        relative_filepaths = [
            os.path.join("ysi_proodo", "somethin"),
            os.path.join("ysi_proodo", "somethin2"),
        ]

        _init_data_dir(
            tmp_path,
            directories_to_include=["ysi_proodo"],
            files_to_include=relative_filepaths,
        )

        expected = [
            os.path.join(tmp_path, "data", relative_filepath)
            for relative_filepath in relative_filepaths
        ]

        actual = module._get_experiment_data_file_paths_for_type(tmp_path, "ysi_proodo")
        assert actual == expected


class TestGetExperimentDataFilesByType:
    def test_returns_series_with_full_file_paths_and_empty_keys(self, tmp_path):
        _init_data_dir(
            tmp_path, ["ysi_prosolo", "ysi_proodo"], ["ysi_prosolo/KorDSS file.csv"]
        )

        expected = pd.Series(
            {
                "setpoints": [],
                "calibration_log": [],
                "pico": [],
                "process_experiment": [],
                "ysi_proodo": [],
                "ysi_prosolo": [
                    os.path.join(tmp_path, "data", "ysi_prosolo", "KorDSS file.csv")
                ],
                "summary_movies": [],
            }
        )

        pd.testing.assert_series_equal(
            module.get_experiment_data_files_by_type(tmp_path), expected
        )
