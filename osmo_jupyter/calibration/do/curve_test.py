import inspect
from itertools import product

import numpy as np
import pytest

import osmo_jupyter.calibration.do.curve as module


class TestDoAndOpticalReadingFunctions:
    @pytest.mark.parametrize(
        'do, temperature',
        list(product(
            [0, 50, 66.12315315, 100],  # DO values
            [15, 20, 28.34912378, 35],  # temperatures
        ))
    )
    def test_estimate_optical_reading_functions_properly_reversed(self, do, temperature):
        optical_reading = module.estimate_optical_reading_two_site_model_with_temperature(
            (do, temperature),
            *module.WORKING_FIT_PARAMS
        )
        round_trip_do = module.estimate_do_two_site_model_with_temperature(
            (optical_reading, temperature),
            *module.WORKING_FIT_PARAMS
        )
        np.testing.assert_almost_equal(
            round_trip_do, do
        )


    @pytest.mark.parametrize('curve_fn', [
        module.estimate_do_two_site_model_with_temperature,
        module.estimate_optical_reading_two_site_model_with_temperature,
    ])
    def test_initial_fit_params_match_function_params(self, curve_fn):
        function_params = list(
            inspect.signature(curve_fn).parameters.keys()
        )
        fit_params = function_params[1:]
        expected_fit_params = list(module.WORKING_FIT_PARAMS_DICT.keys())
        assert fit_params == expected_fit_params


class TestGetArrheniusRate:
    def test_get_arrhenius_rate(self):
        # Spot-check rate function with some actual numbers
        actual = module._get_arrhenius_rate(
            temperature_c=0,
            preexponential_factor=10,
            activation_energy=1e-4
        )
        np.testing.assert_almost_equal(actual, 9.9956, decimal=3)
