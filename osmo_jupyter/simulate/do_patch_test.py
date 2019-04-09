import numpy as np
import pytest

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MIN, TEMPERATURE_STANDARD_OPERATING_MAX
import osmo_jupyter.simulate.do_patch as module


class TestNormalizedReading:
    @pytest.mark.parametrize(
        'name, do, temperature, expected_normalized_reading',
        [
            ('max fluorescence at low DO, low temp', 0, TEMPERATURE_STANDARD_OPERATING_MIN, 1),
            ('min fluorescence at high DO, high temp', 100, TEMPERATURE_STANDARD_OPERATING_MAX, 0),
        ]
    )
    def test_normalized_reading_bounds(self, name, do, temperature, expected_normalized_reading):
        assert module.get_optical_reading_normalized(do, temperature) == expected_normalized_reading

    @pytest.mark.parametrize(
        'name, do, temperature',
        [
            ('middlin DO at min temp', 50, TEMPERATURE_STANDARD_OPERATING_MIN),
            ('middlin DO at max temp', 50, TEMPERATURE_STANDARD_OPERATING_MAX),
            ('max temp at low DO', 0, TEMPERATURE_STANDARD_OPERATING_MAX),
            ('min temp at max DO', 100, TEMPERATURE_STANDARD_OPERATING_MIN),
        ]
    )
    def test_normalized_reading_middlin_values_are_middlin(self, name, do, temperature):
        assert 0 < module.get_optical_reading_normalized(do, temperature) < 1


class TestGetRateConstant:
    def test_get_rate_constant(self):
        # Spot-check rate function with some actual numbers
        actual = module._get_rate_constant(temperature_c=0, preexponential_factor=10, activation_energy=1)
        np.testing.assert_almost_equal(actual, 9.9955975)


class TestEstimateOpticalReading:
    @pytest.mark.parametrize(
        'name, do_pct_sat, temperature_c, expected',
        [
            ('zero DO min temp', 0, TEMPERATURE_STANDARD_OPERATING_MIN, 1.7279002),
            ('zero DO max temp', 0, TEMPERATURE_STANDARD_OPERATING_MAX, 1.2684410),
            ('max DO min temp', 100, TEMPERATURE_STANDARD_OPERATING_MIN, 0.6252858),
            ('max DO max temp', 100, TEMPERATURE_STANDARD_OPERATING_MAX, 0.3969120),
        ]
    )
    def test_estimate_optical_reading(self, name, do_pct_sat, temperature_c, expected):
        # Spot-check function with some actual numbers. This will of course change if we update the curve.
        actual = module._estimate_optical_reading(do_pct_sat, temperature_c)
        np.testing.assert_almost_equal(actual, expected)
