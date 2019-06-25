import pytest
from unittest.mock import call, sentinel

import osmo_jupyter.simulate.do_ratiometric as module


@pytest.fixture
def mock_get_optical_reading_normalized(mocker):
    return mocker.patch.object(module, "get_optical_reading_normalized")


class TestSimulateSpatialRatiometricReading:
    def test_same_do_returns_1(self):
        actual = module.simulate_spatial_ratiometric_reading(
            do=0, temperature=0, sealed_patch_do=0
        )
        assert actual == 1

    def test_unsealed_do_larger_than_sealed_do_returns_less_than_1(self):
        actual = module.simulate_spatial_ratiometric_reading(
            do=50, temperature=0, sealed_patch_do=0
        )
        assert actual < 1

    def test_sealed_do_larger_than_unsealed_do_returns_greater_than_1(self):
        actual = module.simulate_spatial_ratiometric_reading(
            do=0, temperature=0, sealed_patch_do=50
        )
        assert actual > 1

    def test_calls_with_correct_kwargs(self, mock_get_optical_reading_normalized):
        unsealed_patch_kwargs = {"min_value": sentinel.unsealed_min}
        sealed_patch_kwargs = {"min_value": sentinel.sealed_min}

        module.simulate_spatial_ratiometric_reading(
            do=sentinel.do,
            temperature=sentinel.temperature,
            sealed_patch_do=sentinel.sealed_patch_do,
            sealed_patch_kwargs=sealed_patch_kwargs,
            unsealed_patch_kwargs=unsealed_patch_kwargs,
        )

        expected_unsealed_patch_call = call(
            sentinel.do, sentinel.temperature, **unsealed_patch_kwargs
        )
        expected_sealed_patch_call = call(
            sentinel.sealed_patch_do, sentinel.temperature, **sealed_patch_kwargs
        )

        mock_get_optical_reading_normalized.assert_has_calls(
            [expected_unsealed_patch_call, expected_sealed_patch_call]
        )

    def test_returns_ratio_of_unsealed_to_sealed(
        self, mock_get_optical_reading_normalized
    ):
        mock_optical_reading_for_unsealed_patch = 1
        mock_optical_reading_for_sealed_patch = 2

        # Set up the mock to return "1" the first time (when it is called for the *unsealed* patch)
        # and "2" the second (when it is called for the *sealed* patch)
        mock_get_optical_reading_normalized.side_effect = [
            mock_optical_reading_for_unsealed_patch,
            mock_optical_reading_for_sealed_patch,
        ]

        actual = module.simulate_spatial_ratiometric_reading(
            do=sentinel.do,
            temperature=sentinel.temperature,
            sealed_patch_do=sentinel.sealed_patch_do,
        )

        assert actual == (
            mock_optical_reading_for_unsealed_patch
            / mock_optical_reading_for_sealed_patch
        )
