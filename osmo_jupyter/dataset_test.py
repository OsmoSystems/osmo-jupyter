import pandas as pd
import pytest

import osmo_jupyter.dataset as module

TEST_YSI_CSV_DATA = pd.DataFrame(
    [
        {
            "Timestamp": "2019-01-01 00:00:00",
            "Barometer (mmHg)": 750,
            "Dissolved Oxygen (%)": 19,
            "Temperature (C)": 24.7,
            "Unit ID": "unit ID",
            "Comment": None,
            "Site": None,
            "Folder": None,
        }
    ]
)

TEST_YSI_KORDSS_DATA = pd.DataFrame(
    [
        {
            "DATE": "2019-01-01",
            "TIME": "00:00:00",
            "Barometer (mmHg)": 750,
            "ODO (% Sat)": 60,
            "ODO (mg/L)": 6,
            "Temp (°C)": 24.7,
            "SITE": None,
            "DATA ID": None,
            "ODO (% Local)": 60,
        }
    ]
)

TEST_PICOLOG_DATA = pd.DataFrame(
    [
        {
            "": "2019-01-01T00:00:00-07:00",
            "Temperature Ave. (C)": 39,
            "Pressure (Voltage) Ave. (nV)": 10,
        },
        {
            "": "2019-01-01T00:00:02-07:00",
            "Temperature Ave. (C)": 40,
            "Pressure (Voltage) Ave. (nV)": 10,
        },
        {
            "": "2019-01-01T00:00:04-07:00",
            "Temperature Ave. (C)": 40,
            "Pressure (Voltage) Ave. (nV)": 10,
        },
    ]
)

TEST_CALIBRATION_DATA = pd.DataFrame(
    [
        {
            "timestamp": "2019-01-01 00:00:00.1",
            "equilibration status": "waiting",
            "setpoint temperature": 40,
        },
        {
            "timestamp": "2019-01-01 00:00:01.1",
            "equilibration status": "equilibrated",
            "setpoint temperature": 40,
        },
        {
            "timestamp": "2019-01-01 00:00:03.1",
            "equilibration status": "equilibrated",
            "setpoint temperature": 40,
        },
        {
            "timestamp": "2019-01-01 00:00:04.1",
            "equilibration status": "waiting",
            "setpoint temperature": 40,
        },
    ]
)


TEST_PROCESS_EXPERIMENT_DATA = pd.DataFrame(
    [
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
            "image": "image-0.jpeg",
            "ROI": "ROI 0",
            "r_msorm": 0.5,
            "g_msorm": 0.4,
        },
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
            "image": "image-0.jpeg",
            "ROI": "ROI 1",
            "r_msorm": 0.4,
            "g_msorm": 0.5,
        },
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
            "image": "image-1.jpeg",
            "ROI": "ROI 0",
            "r_msorm": 0.3,
            "g_msorm": 0.6,
        },
        {
            "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
            "image": "image-1.jpeg",
            "ROI": "ROI 1",
            "r_msorm": 0.6,
            "g_msorm": 0.3,
        },
    ]
)


def create_mock_file_obj(tmpdir, data, file_name):
    mock_file_obj = tmpdir.join(file_name)
    data.to_csv(mock_file_obj, index=False)

    return mock_file_obj


@pytest.fixture
def mock_picolog_file_obj(tmpdir):
    return create_mock_file_obj(tmpdir, TEST_PICOLOG_DATA, "test_pico_data.csv")


@pytest.fixture
def mock_calibration_file_obj(tmpdir):
    return create_mock_file_obj(
        tmpdir, TEST_CALIBRATION_DATA, "test_calibration_data.csv"
    )


class TestReadAndFormatDataFile:
    def test_formats_ysi_csv_correctly(self, tmpdir):
        mock_YSI_csv_file_obj = create_mock_file_obj(
            tmpdir, TEST_YSI_CSV_DATA, "test_ysi.csv"
        )

        formatted_ysi_data = module.parse_ysi_classic_file(mock_YSI_csv_file_obj)
        expected_ysi_data = pd.DataFrame(
            [
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                    "YSI barometric pressure (mmHg)": 750,
                    "YSI DO (%)": 19,
                    "YSI temperature (C)": 24.7,
                    "YSI unit ID": "unit ID",
                }
            ]
        ).set_index("timestamp")

        pd.testing.assert_frame_equal(formatted_ysi_data, expected_ysi_data)

    def test_formats_ysi_kordss_correctly(self, tmpdir):
        mock_YSI_KorDSS_file_obj = tmpdir.join("test_kordss.csv")
        mock_YSI_KorDSS_file_obj.write("\n\n\n\n\n")
        TEST_YSI_KORDSS_DATA.to_csv(
            mock_YSI_KorDSS_file_obj, index=False, mode="a", encoding="latin-1"
        )

        formatted_ysi_data = module.parse_ysi_kordss_file(mock_YSI_KorDSS_file_obj)
        expected_ysi_data = pd.DataFrame(
            [
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                    "YSI barometric pressure (mmHg)": 750,
                    "YSI DO (%)": 60,
                    "YSI DO (mg/L)": 6,
                    "YSI temperature (C)": 24.7,
                }
            ]
        ).set_index("timestamp")

        pd.testing.assert_frame_equal(formatted_ysi_data, expected_ysi_data)

    def test_formats_picolog_csv_correctly(self, mock_picolog_file_obj):
        formatted_picolog_data = module.parse_picolog_file(mock_picolog_file_obj)
        expected_picolog_data = pd.DataFrame(
            [
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                    "PicoLog temperature (C)": 39,
                },
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
                    "PicoLog temperature (C)": 40,
                },
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:04"),
                    "PicoLog temperature (C)": 40,
                },
            ]
        ).set_index("timestamp")

        pd.testing.assert_frame_equal(formatted_picolog_data, expected_picolog_data)

    def test_formats_calibration_log_correctly(self, mock_calibration_file_obj):
        formatted_calibration_log_data = module.parse_calibration_log_file(
            mock_calibration_file_obj
        )
        # Nothing is supposed to be renamed or dropped, just datetime formatting
        expected_calibration_log_data = pd.DataFrame(
            [
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                    "equilibration status": "waiting",
                    "setpoint temperature": 40,
                },
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:01"),
                    "equilibration status": "equilibrated",
                    "setpoint temperature": 40,
                },
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:03"),
                    "equilibration status": "equilibrated",
                    "setpoint temperature": 40,
                },
                {
                    "timestamp": pd.to_datetime("2019-01-01 00:00:04"),
                    "equilibration status": "waiting",
                    "setpoint temperature": 40,
                },
            ]
        ).set_index("timestamp")

        pd.testing.assert_frame_equal(
            formatted_calibration_log_data, expected_calibration_log_data
        )


class TestOpenAndCombineSensorData:
    def test_interpolates_data_correctly(
        self, mock_calibration_file_obj, mock_picolog_file_obj
    ):
        combined_data = module.open_and_combine_picolog_and_calibration_data(
            calibration_log_filepaths=[mock_calibration_file_obj],
            picolog_log_filepaths=[mock_picolog_file_obj],
        ).reset_index()  # move timestamp index to a column

        expected_interpolation = pd.DataFrame(
            [
                {
                    "timestamp": "2019-01-01 00:00:00",
                    "equilibration status": "waiting",
                    "setpoint temperature": 40,
                    "PicoLog temperature (C)": 39,
                },
                {
                    "timestamp": "2019-01-01 00:00:01",
                    "equilibration status": "equilibrated",
                    "setpoint temperature": 40,
                    "PicoLog temperature (C)": 39.5,
                },
                {
                    "timestamp": "2019-01-01 00:00:03",
                    "equilibration status": "equilibrated",
                    "setpoint temperature": 40,
                    "PicoLog temperature (C)": 40,
                },
                {
                    "timestamp": "2019-01-01 00:00:04",
                    "equilibration status": "waiting",
                    "setpoint temperature": 40,
                    "PicoLog temperature (C)": 40,
                },
            ]
        ).astype(
            combined_data.dtypes
        )  # coerce datatypes to match

        pd.testing.assert_frame_equal(combined_data, expected_interpolation)


class TestGetEquilibrationBoundaries:
    @pytest.mark.parametrize(
        "input_equilibration_status, expected_boundaries",
        [
            (
                {  # Use full timestamps to show that it works at second resolution
                    pd.to_datetime("2019-01-01 00:00:00"): "waiting",
                    pd.to_datetime("2019-01-01 00:00:01"): "equilibrated",
                    pd.to_datetime("2019-01-01 00:00:02"): "equilibrated",
                    pd.to_datetime("2019-01-01 00:00:03"): "waiting",
                },
                [
                    {
                        "start_time": pd.to_datetime("2019-01-01 00:00:01"),
                        "end_time": pd.to_datetime("2019-01-01 00:00:02"),
                    }
                ],
            ),
            (
                {  # Switch to using only years as the timestamp for terseness and readability
                    pd.to_datetime("2019"): "waiting",
                    pd.to_datetime("2020"): "equilibrated",
                    pd.to_datetime("2021"): "waiting",
                },
                [
                    {
                        "start_time": pd.to_datetime("2020"),
                        "end_time": pd.to_datetime("2020"),
                    }
                ],
            ),
            (
                {
                    pd.to_datetime("2020"): "equilibrated",
                    pd.to_datetime("2021"): "waiting",
                    pd.to_datetime("2022"): "equilibrated",
                    pd.to_datetime("2023"): "waiting",
                },
                [
                    {
                        "start_time": pd.to_datetime("2020"),
                        "end_time": pd.to_datetime("2020"),
                    },
                    {
                        "start_time": pd.to_datetime("2022"),
                        "end_time": pd.to_datetime("2022"),
                    },
                ],
            ),
            (
                {
                    pd.to_datetime("2019"): "waiting",
                    pd.to_datetime("2020"): "equilibrated",
                    pd.to_datetime("2021"): "waiting",
                    pd.to_datetime("2022"): "equilibrated",
                },
                [
                    {
                        "start_time": pd.to_datetime("2020"),
                        "end_time": pd.to_datetime("2020"),
                    },
                    {
                        "start_time": pd.to_datetime("2022"),
                        "end_time": pd.to_datetime("2022"),
                    },
                ],
            ),
            (
                {
                    pd.to_datetime("2019"): "waiting",
                    pd.to_datetime("2020"): "equilibrated",
                    pd.to_datetime("2021"): "waiting",
                    pd.to_datetime("2022"): "equilibrated",
                    pd.to_datetime("2023"): "waiting",
                },
                [
                    {
                        "start_time": pd.to_datetime("2020"),
                        "end_time": pd.to_datetime("2020"),
                    },
                    {
                        "start_time": pd.to_datetime("2022"),
                        "end_time": pd.to_datetime("2022"),
                    },
                ],
            ),
            (
                {
                    pd.to_datetime("2019"): "equilibrated",
                    pd.to_datetime("2020"): "waiting",
                },
                [
                    {
                        "start_time": pd.to_datetime("2019"),
                        "end_time": pd.to_datetime("2019"),
                    }
                ],
            ),
            (
                {
                    pd.to_datetime("2019"): "waiting",
                    pd.to_datetime("2020"): "equilibrated",
                },
                [
                    {
                        "start_time": pd.to_datetime("2020"),
                        "end_time": pd.to_datetime("2020"),
                    }
                ],
            ),
            (
                {
                    pd.to_datetime("2019"): "equilibrated",
                    pd.to_datetime("2020"): "waiting",
                    pd.to_datetime("2021"): "equilibrated",
                },
                [
                    {
                        "start_time": pd.to_datetime("2019"),
                        "end_time": pd.to_datetime("2019"),
                    },
                    {
                        "start_time": pd.to_datetime("2021"),
                        "end_time": pd.to_datetime("2021"),
                    },
                ],
            ),
        ],
    )
    def test_finds_correct_edges(self, input_equilibration_status, expected_boundaries):

        parsed_equilibration_boundaries = module.get_equilibration_boundaries(
            equilibration_status=pd.Series(input_equilibration_status)
        )

        expected_equilibration_boundaries = pd.DataFrame(
            expected_boundaries,
            columns=["start_time", "end_time"],
            dtype="datetime64[ns]",
        ).reset_index(
            drop=True
        )  # Coerce to a RangeIndex when creating empty DataFrame

        pd.testing.assert_frame_equal(
            parsed_equilibration_boundaries, expected_equilibration_boundaries
        )


class TestPivotProcessExperimentResults:
    def test_combines_image_rows_by_ROI(self):
        pivot_results = module.pivot_process_experiment_results_on_ROI(
            experiment_df=TEST_PROCESS_EXPERIMENT_DATA,
            ROI_names=list(TEST_PROCESS_EXPERIMENT_DATA["ROI"].unique()),
            msorm_types=["r_msorm", "g_msorm"],
        )

        expected_results_data = (
            pd.DataFrame(
                [
                    {
                        "timestamp": pd.to_datetime("2019-01-01 00:00:00"),
                        "ROI 0 r_msorm": 0.5,
                        "ROI 1 r_msorm": 0.4,
                        "ROI 0 g_msorm": 0.4,
                        "ROI 1 g_msorm": 0.5,
                        "image": "image-0.jpeg",
                    },
                    {
                        "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
                        "ROI 0 r_msorm": 0.3,
                        "ROI 1 r_msorm": 0.6,
                        "ROI 0 g_msorm": 0.6,
                        "ROI 1 g_msorm": 0.3,
                        "image": "image-1.jpeg",
                    },
                ]
            )
            .set_index("timestamp")
            .astype(pivot_results.dtypes)
        )

        pd.testing.assert_frame_equal(pivot_results, expected_results_data)


class TestGetAllExperimentImages:
    def test_returns_only_image_files(self, mocker):
        image_file_name = "image-0.jpeg"
        experiment_name = "test"

        mocker.patch("os.listdir", return_value=[image_file_name, "experiment.log"])

        experiment_images = module.get_all_experiment_images(
            local_sync_directory="", experiment_names=[experiment_name]
        )

        expected_images = pd.DataFrame(
            [{"experiment": experiment_name, "image": image_file_name}]
        )

        pd.testing.assert_frame_equal(experiment_images, expected_images)

    def test_has_correct_dtype_when_no_images_found(self, mocker):
        mocker.patch("os.listdir", return_value=[])

        experiment_images = module.get_all_experiment_images(
            local_sync_directory="", experiment_names=["test"]
        )

        pd.testing.assert_frame_equal(
            experiment_images,
            pd.DataFrame(columns=["experiment", "image"], dtype="object"),
        )


class TestFilterEquilibratedImages:
    def test_returns_only_equilibrated_images(self, mock_calibration_file_obj):
        test_roi_data = pd.DataFrame(
            [
                {"timestamp": pd.to_datetime("2019-01-01"), "image": "image-0.jpeg"},
                {"timestamp": pd.to_datetime("2019-01-03"), "image": "image-1.jpeg"},
            ]
        ).set_index("timestamp")

        test_equilibration_boundaries = pd.Series(
            {
                "start_time": pd.to_datetime("2019-01-02"),
                "end_time": pd.to_datetime("2019-01-04"),
            }
        )

        equilibrated_image_data = module.filter_equilibrated_images(
            equilibration_range=test_equilibration_boundaries, df=test_roi_data
        )

        expected_equilibrated_image_data = test_roi_data[1:]

        pd.testing.assert_frame_equal(
            equilibrated_image_data, expected_equilibrated_image_data
        )


class TestOpenAndCombineSourceData:
    def test_filters_all_data_to_equilibrated_states(
        self, mocker, mock_calibration_file_obj, mock_picolog_file_obj
    ):
        test_files = ["image-0.jpeg", "image-1.jpeg", "experiment.log"]
        mocker.patch("os.listdir", return_value=test_files)

        mocker.patch.object(
            module,
            "open_and_combine_process_experiment_results",
            return_value=module.pivot_process_experiment_results_on_ROI(
                experiment_df=TEST_PROCESS_EXPERIMENT_DATA,
                ROI_names=list(TEST_PROCESS_EXPERIMENT_DATA["ROI"].unique()),
                msorm_types=["r_msorm", "g_msorm"],
            ),
        )

        experiment_name = "test"

        equilibrated_experiment_data = module.open_and_combine_and_filter_source_data(
            local_sync_directory="",
            experiment_names=[experiment_name],
            calibration_log_filepaths=[mock_calibration_file_obj],
            picolog_log_filepaths=[mock_picolog_file_obj],
            process_experiment_result_filepaths=[],
        )

        expected_experiment_data = (
            pd.DataFrame(
                [
                    {
                        "timestamp": pd.to_datetime("2019-01-01 00:00:02"),
                        "ROI 0 r_msorm": 0.3,
                        "ROI 1 r_msorm": 0.6,
                        "ROI 0 g_msorm": 0.6,
                        "ROI 1 g_msorm": 0.3,
                        "image": "image-1.jpeg",
                        "PicoLog temperature (C)": 40,
                        "setpoint temperature": 40,
                        "experiment": experiment_name,
                    }
                ]
            )
            .set_index("image")
            .astype(equilibrated_experiment_data.dtypes)
        )

        pd.testing.assert_frame_equal(
            equilibrated_experiment_data, expected_experiment_data
        )
