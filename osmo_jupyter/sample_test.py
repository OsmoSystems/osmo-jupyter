import numpy as np
import pandas as pd

import osmo_jupyter.sample as module


class TestSampleUniform(object):
    small_test_dataframe = pd.DataFrame(
        [
            # Add some balanced data
            (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 1), (3, 2), (3, 3), (3, 4),
            (4, 1), (4, 2), (4, 3), (4, 4),
            # Unbalance with some extra values
            (1, 1), (1, 1), (1, 2), (1, 2),
        ],
        columns=['one', 'two']
    )

    def test_sampling_on_one_dimension(self):
        num_bins = 4

        output_dataframe = module.uniform(
            self.small_test_dataframe,
            columns_and_bin_counts={
                'one': num_bins
            },
        )

        expected_distribution = np.full(num_bins, 1 / num_bins)
        actual_distribution = output_dataframe['one'].value_counts(normalize=True).values

        np.testing.assert_almost_equal(actual_distribution, expected_distribution)

    def test_bin_count_saturates_at_unique_value_count(self):
        num_bins = 4000

        output_dataframe = module.uniform(
            self.small_test_dataframe,
            columns_and_bin_counts={
                'one': num_bins
            },
        )

        unique_values_count = len(self.small_test_dataframe['one'].unique())
        expected_distribution = np.full(unique_values_count, 1 / unique_values_count)

        actual_distribution = output_dataframe['one'].value_counts(normalize=True).values

        np.testing.assert_almost_equal(actual_distribution, expected_distribution)

    def test_sampling_on_multiple_dimensions(self):
        num_bins = 7
        num_columns = 10
        columns = [f'column_{n}' for n in range(0, num_columns)]
        columns_to_balance = columns[0:4]
        input_dataframe = pd.DataFrame(
            np.random.rand(10000, num_columns),
            columns=columns
        )

        output_dataframe = module.uniform(
            input_dataframe,
            columns_and_bin_counts={
                column: num_bins for column in columns_to_balance
            }
        )

        expected_distribution = np.full(num_bins, 1 / num_bins)

        for column in columns_to_balance:
            actual_distribution = pd.cut(
                output_dataframe[column],
                num_bins
            ).value_counts(normalize=True).values

            np.testing.assert_almost_equal(
                actual_distribution,
                expected_distribution,
                decimal=2
            )

    def test_sampled_rows_match_input_rows(self):
        num_columns = 4
        columns = [f'column_{n}' for n in range(0, num_columns)]
        input_dataframe = pd.DataFrame(
            np.random.rand(1000, num_columns),
            columns=columns
        )

        output_dataframe = module.uniform(
            input_dataframe,
            columns_and_bin_counts={
                'column_1': 10,
                'column_2': 10
            }
        )

        pd.testing.assert_frame_equal(
            input_dataframe.loc[output_dataframe.index],
            output_dataframe
        )
