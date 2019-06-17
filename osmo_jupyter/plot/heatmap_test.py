from unittest.mock import sentinel

import numpy as np
import pytest

from . import heatmap as module


class TestCutArray2D:
    def test_cut_odd_shape(self):
        odd_array = np.array(
            [
                [1, 1, 1, 2, 2, 2, 3, 3, 3],
                [1, 1, 1, 2, 2, 2, 3, 3, 3],
                [1, 1, 1, 2, 2, 2, 3, 3, 3],
            ]
        )

        expected_block_centers = [(1, 1), (1, 4), (1, 7)]
        expected_blocks = np.array(
            [
                [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
                [[2, 2, 2], [2, 2, 2], [2, 2, 2]],
                [[3, 3, 3], [3, 3, 3], [3, 3, 3]],
            ]
        )

        actual_block_centers, actual_blocks = module.cut_array2d(
            odd_array, block_shape=(3, 3)
        )

        np.testing.assert_array_equal(actual_block_centers, expected_block_centers)
        np.testing.assert_array_equal(actual_blocks, expected_blocks)

    def test_cut_even_shape(self):
        even_array = np.array([[1, 1, 2, 2], [1, 1, 2, 2], [3, 3, 4, 4], [3, 3, 4, 4]])

        expected_block_centers = [(0.5, 0.5), (0.5, 2.5), (2.5, 0.5), (2.5, 2.5)]
        expected_blocks = np.array(
            [[[1, 1], [1, 1]], [[2, 2], [2, 2]], [[3, 3], [3, 3]], [[4, 4], [4, 4]]]
        )

        actual_block_centers, actual_blocks = module.cut_array2d(
            even_array, block_shape=(2, 2)
        )

        np.testing.assert_array_equal(actual_block_centers, expected_block_centers)
        np.testing.assert_array_equal(actual_blocks, expected_blocks)

    def test_mismatch_shape_drops_edges(self):
        mismatch_shaped_array = np.array([[1, 1, 2], [1, 1, 2], [2, 2, 2]])

        actual_block_centers, actual_blocks = module.cut_array2d(
            mismatch_shaped_array, block_shape=(2, 2)
        )

        expected_block_centers = [(0.5, 0.5)]
        expected_blocks = np.array([[[1, 1], [1, 1]]])

        np.testing.assert_array_equal(actual_block_centers, expected_block_centers)
        np.testing.assert_array_equal(actual_blocks, expected_blocks)

    def test_maintains_order_within_block(self):
        mismatch_shaped_array = np.array([[1, 2, 5, 6], [3, 4, 7, 8]])

        actual_block_centers, actual_blocks = module.cut_array2d(
            mismatch_shaped_array, block_shape=(2, 2)
        )

        expected_block_centers = [(0.5, 0.5), (0.5, 2.5)]
        expected_blocks = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

        np.testing.assert_array_equal(actual_block_centers, expected_block_centers)
        np.testing.assert_array_equal(actual_blocks, expected_blocks)

    def test_returns_nothing_if_block_size_larger_than_array(self):
        small_array = np.array([[1, 1, 1], [1, 1, 1]])

        actual_block_centers, actual_blocks = module.cut_array2d(
            small_array, block_shape=(3, 3)
        )

        np.testing.assert_array_equal(actual_block_centers, [])
        np.testing.assert_array_equal(actual_blocks, [])


class TestGetBlockMeans2D:
    def test_gets_block_means(self):
        actual = module.get_block_means_2d(
            block_centers=[(0.5, 0.5), (0.5, 2.5)],
            blocks=np.array([[[1, 2], [3, 4]], [[10, 20], [30, 40]]]),
        )

        expected = np.array([[2.5, 25.0]])

        np.testing.assert_array_equal(actual, expected)

    def test_reshapes_to_match_block_centers(self):
        actual = module.get_block_means_2d(
            block_centers=[(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)],
            blocks=[[1], [2], [3], [4], [5], [6]],
        )

        expected = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

        np.testing.assert_array_equal(actual, expected)

    def test_uses_provided_averaging_function(self):
        def _mock_averaging_func(array):
            return sentinel.averaged

        actual = module.get_block_means_2d(
            block_centers=[(0.5, 0.5), (0.5, 2.5)],
            blocks=np.array([[[1, 2], [2, 3]], [[10, 11], [11, 30]]]),
            averaging_function=_mock_averaging_func,
        )

        expected = np.array([[sentinel.averaged, sentinel.averaged]])

        np.testing.assert_array_equal(actual, expected)

    @pytest.mark.parametrize(
        "name,block_centers,blocks",
        [
            ("too many blocks", [(1, 1), (1, 2), (1, 3)], [[1], [2], [3], [4]]),
            ("too many block centers", [(1, 1), (1, 2), (1, 3)], [[1], [2]]),
            ("empty blocks", [(1, 1), (1, 2), (1, 3)], []),
            ("empty block centers", [], [[1], [2], [3]]),
        ],
    )
    def test_raises_on_mismatched_size(self, name, block_centers, blocks):
        with pytest.raises(ValueError):
            module.get_block_means_2d(block_centers, blocks)


@pytest.fixture
def mock_display_heatmap(mocker):
    return mocker.patch.object(module, "display_heatmap")


class TestHeatmapify:
    def test_heatmapify(self, mock_display_heatmap):
        array = np.array(
            [
                [1, 1, 1, 2, 2, 2, 3, 3, 3],
                [1, 1, 1, 2, 2, 2, 3, 3, 3],
                [1, 1, 1, 2, 2, 2, 3, 3, 3],
            ]
        )

        expected_block_means_2d = [[1.0, 2.0, 3.0]]

        module.heatmapify(array, block_shape=(3, 3))

        # call_args is a tuple of ((positional arguments), (kwargs))
        actual_block_means_2d = mock_display_heatmap.call_args[0][0]

        np.testing.assert_array_equal(actual_block_means_2d, expected_block_means_2d)
