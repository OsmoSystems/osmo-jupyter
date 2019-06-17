import numpy
import pytest

import osmo_jupyter.plot.do_calibration as module


class TestGetRSquared:
    def test_perfect_model_gets_perfect_score(self):
        y_data = numpy.array([1, 2, 3])
        actual = module._get_r_squared(predicted=y_data, actual=y_data)
        expected = 1
        assert actual == expected

    def test_slightly_imperfect_model_gets_less_than_perfect_score(self):
        actual = module._get_r_squared(
            predicted=numpy.array([1, 2, 3]), actual=numpy.array([1, 2, 2.9])
        )
        assert 0 < actual < 1

    def test_bad_model_gets_negative_score(self):
        actual = module._get_r_squared(
            # Prediction is anticorrelated with actual -> r-squared should be negative.
            predicted=numpy.array([1, 2, 3]),
            actual=numpy.array([3, 2, 1]),
        )
        assert actual < 0


class TestGetAdjustedRSquared:
    def test_perfect_model_gets_perfect_score(self):
        y_data = numpy.array([1, 2, 3, 4])
        actual = module._get_adjusted_r_squared(predicted=y_data, actual=y_data, p=2)
        expected = 1
        assert actual == expected

    def test_model_penalized_for_larger_p(self):
        predicted_y = numpy.array([1, 2, 3, 4, 5])
        actual_y = numpy.array([1, 2, 2.9, 4, 5])

        score_with_p_1 = module._get_adjusted_r_squared(
            predicted=predicted_y, actual=actual_y, p=2
        )

        score_with_p_2 = module._get_adjusted_r_squared(
            predicted=predicted_y, actual=actual_y, p=3
        )
        assert score_with_p_1 > score_with_p_2

    def test_blows_up_with_n_less_than_p_minus_one(self):
        y_data = numpy.array([1, 2, 3])

        with pytest.raises(ValueError):
            module._get_adjusted_r_squared(predicted=y_data, actual=y_data, p=2)
