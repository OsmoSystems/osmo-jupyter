import os
from pathlib import Path

import pytest
import pandas as pd

import osmo_jupyter.dataset.source_files as module


@pytest.fixture
def mock_get_experiment_filenames_from_s3(mocker):
    return mocker.patch.object(module, "_get_experiment_filenames_from_s3")


def _init_data_dir(parent_dir: Path, directories_to_include, files_to_include):
    """set up a data directory with folders and files in it
    Args:
        parent_dir: Path object that everything's expected to be under
        directories_to_include: iterable of directory names to initialize
        files_to_include: iterable of file names to initialize. If they are in subdirectories,
            the subdirectories should be listed in directories_to_include to be created first
    """
    data_dir = parent_dir / "data"
    data_dir.mkdir()

    for relative_directory_path in directories_to_include:
        (data_dir / relative_directory_path).mkdir(parents=True)

    for relative_file_path in files_to_include:
        (data_dir / relative_file_path).touch()


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
            directories_to_include=[Path("ysi_proodo") / "subdirectory"],
            files_to_include=[Path("ysi_proodo") / "somethin.csv"],
        )
        actual = module._get_experiment_data_file_paths_for_type(tmp_path, "ysi_proodo")
        expected = [tmp_path / "data" / "ysi_proodo" / "somethin.csv"]
        assert actual == expected

    def test_gets_multiple_files(self, tmp_path):
        relative_filepaths = [
            os.path.join("ysi_proodo", "somethin.csv"),
            os.path.join("ysi_proodo", "somethin2.csv"),
        ]

        _init_data_dir(
            tmp_path,
            directories_to_include=["ysi_proodo"],
            files_to_include=relative_filepaths,
        )

        expected = [
            tmp_path / "data" / relative_filepath
            for relative_filepath in relative_filepaths
        ]

        actual = module._get_experiment_data_file_paths_for_type(tmp_path, "ysi_proodo")
        assert actual == expected

    def test_ignores_unwanted_filetypes(self, tmp_path):
        relative_filepaths = [
            os.path.join("ysi_proodo", "somethin.csv"),
            os.path.join("ysi_proodo", "somethin2.xlsx"),
        ]

        _init_data_dir(
            tmp_path,
            directories_to_include=["ysi_proodo"],
            files_to_include=relative_filepaths,
        )

        expected = [tmp_path / "data" / relative_filepaths[0]]

        actual = module._get_experiment_data_file_paths_for_type(tmp_path, "ysi_proodo")
        assert actual == expected


class TestGetExperimentDataFilesByType:
    def test_returns_series_with_full_file_paths_and_empty_keys(self, tmp_path):
        _init_data_dir(
            tmp_path,
            ["ysi_prosolo", "ysi_proodo"],
            [Path("ysi_prosolo") / "KorDSS file.csv"],
        )

        expected = pd.Series(
            {
                "setpoints": [],
                "calibration_log": [],
                "pico": [],
                "process_experiment": [],
                "ysi_proodo": [],
                "ysi_prosolo": [tmp_path / "data" / "ysi_prosolo" / "KorDSS file.csv"],
                "summary_movies": [],
            }
        )

        pd.testing.assert_series_equal(
            module.get_experiment_data_files_by_type(tmp_path), expected
        )


class TestGetAllExperimentImages:
    def test_returns_only_image_files(self, mock_get_experiment_filenames_from_s3):
        image_file_name = "image-0.jpeg"
        experiment_name = "test"

        mock_get_experiment_filenames_from_s3.return_value = [
            image_file_name,
            "experiment.log",
        ]

        experiment_images = module.get_all_experiment_image_filenames(
            experiment_names=[experiment_name]
        )

        expected_images = pd.DataFrame(
            [{"experiment_name": experiment_name, "image_filename": image_file_name}]
        )

        pd.testing.assert_frame_equal(experiment_images, expected_images)

    def test_has_correct_dtype_when_no_images_found(
        self, mock_get_experiment_filenames_from_s3
    ):
        mock_get_experiment_filenames_from_s3.return_value = []

        experiment_images = module.get_all_experiment_image_filenames(
            experiment_names=["test"]
        )

        pd.testing.assert_frame_equal(
            experiment_images,
            pd.DataFrame(columns=["experiment_name", "image_filename"], dtype="object"),
        )
