import pandas as pd

import .normalize as module


def test_normalize_to_max():
    dataframe = pd.DataFrame({
        'column a': [1, 2, 3],
        'column b': [8, 10, 9],
    })
    expected = pd.DataFrame({
        'column a': [1/3, 2/3, 1],
        'column b': [.8, 1, .9],
    })

    actual = module.to_max(dataframe)
    assert pd.testing.assert_frame_equal(actual, expected)


def test_normalize_by_rgb_sum():
    dataframe = pd.DataFrame({
        'r': [1, 2, 3],
        'g': [5, 6, 7],
        'b': [8, 10, 9],
    })
    expected = pd.DataFrame({
        'r': [1/14, 2/18, 3/19],
        'g': [5/14, 6/18, 7/19],
        'b': [8/14, 10/18, 9/19],
    })

    actual = module.to_max(dataframe)
    assert pd.testing.assert_frame_equal(actual, expected)
