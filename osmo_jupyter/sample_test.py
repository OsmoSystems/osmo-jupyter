import numpy as np
import pandas as pd

import osmo_jupyter.sample as module


class TestSampleUniform(object):
    small_test_dataframe = pd.DataFrame(
        [
            (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 1), (3, 2), (3, 3), (3, 4),
            (4, 1), (4, 2), (4, 3), (4, 4),

            (1, 1), (1, 1), (1, 2), (1, 2),
        ],
        columns=['one', 'two']
    )

    def test_uniform_in_one_dimension(self):
        num_bins = 4

        output_dataframe = module.uniform(
            self.small_test_dataframe,
            columns=['one'],
            bin_counts=[num_bins]
        )

        col_1_distribution = output_dataframe['one'].value_counts(normalize=True).values
        np.testing.assert_almost_equal(col_1_distribution, np.full(num_bins, 1 / num_bins))

    def test_uniform_with_extra_bins(self):
        num_bins = 4000

        output_dataframe = module.uniform(
            self.small_test_dataframe,
            columns=['one'],
            bin_counts=[num_bins]
        )

        num_unique = len(self.small_test_dataframe['one'].unique())
        col_1_distribution = output_dataframe['one'].value_counts(normalize=True).values
        np.testing.assert_almost_equal(col_1_distribution, np.full(num_unique, 1 / num_unique))

    def test_uniform_in_multiple_dimensions(self):
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
            columns=columns_to_balance,
            bin_counts=[num_bins] * len(columns_to_balance)
        )

        for column in columns_to_balance:
            distribution = pd.cut(
                output_dataframe[column],
                num_bins
            ).value_counts(normalize=True).values

            np.testing.assert_almost_equal(
                distribution,
                np.full(num_bins, 1 / num_bins),
                decimal=2
            )
