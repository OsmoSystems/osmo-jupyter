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
