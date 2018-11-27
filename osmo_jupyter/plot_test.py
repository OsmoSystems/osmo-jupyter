import pandas as pd
import pytest

import osmo_jupyter.plot as module


class TestGetColorsWithPattern:
    def test_basic_case(self):
        assert module._get_colors_with_pattern('*_mean') == ['r_mean', 'g_mean', 'b_mean']

    def test_missing_asterisk__blows_up_helpfully(self):
        with pytest.raises(ValueError, match=r'does not contain an asterisk'):
            module._get_colors_with_pattern('lololololol')


class TestGetRgbColumns:
    def test_basic_case(self):
        orig_df = pd.DataFrame({
            'r_abcd': [1, 2, 3],
            'g_abcd': [4, 5, 6],
            'b_abcd': [7, 8, 9],
            'other': [10, 11, 12]
        })

        actual = module.get_rgb_columns(orig_df, '*_abcd')

        expected = pd.DataFrame({
            'r': orig_df['r_abcd'],
            'g': orig_df['g_abcd'],
            'b': orig_df['b_abcd'],
        })

        pd.testing.assert_frame_equal(actual, expected)


class TestAddRgbColumns:
    rgb_df = pd.DataFrame({
        'r': [1, 2, 3],
        'g': [4, 5, 6],
        'b': [7, 8, 9],
    })

    def test_basic_case(self):
        orig_df = pd.DataFrame({
            'other': [10, 11, 12]
        })
        module.add_rgb_columns(orig_df, self.rgb_df, '*_abcd')

        expected = pd.DataFrame({
            'other': orig_df['other'],
            'r_abcd': self.rgb_df['r'],
            'g_abcd': self.rgb_df['g'],
            'b_abcd': self.rgb_df['b'],
        })

        pd.testing.assert_frame_equal(orig_df, expected)

    def test_missing_rgb_column__blows_up(self):
        orig_df = pd.DataFrame({
            'other': [10, 11, 12]
        })

        rgb_df_with_missing_color = self.rgb_df[['r', 'g']]
        with pytest.raises(Exception):
            module.add_rgb_columns(orig_df, rgb_df_with_missing_color, '*_abcd')
