import numpy as np
import pandas as pd

import osmo_jupyter.sample as module


def create_dataframe_with_one_outlier():
    '''
    Generates a large 1-column dataframe of random values with a single outlier
    '''
    np.random.seed(0)
    # Generate an array of 10000 values between 0-98
    random_data = np.random.randint(0, 99, (10000, 1))
    # Add one value of 99
    data_with_outlier = np.append(random_data, [99])
    return pd.DataFrame(data_with_outlier, columns=['one'])


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

        # Use normalized value_counts to get the distribution of values in column 'one'
        actual_distribution = output_dataframe['one'].value_counts(normalize=True).values
        # Create an array of expected value count distribution in column 'one'
        expected_distribution = np.full(num_bins, 1 / num_bins)

        np.testing.assert_almost_equal(actual_distribution, expected_distribution)

    def test_bin_count_saturates_at_unique_value_count(self):
        num_bins = 4000

        output_dataframe = module.uniform(
            self.small_test_dataframe,
            columns_and_bin_counts={
                'one': num_bins
            },
        )

        # Use normalized value_counts to get the distribution of values in column 'one'
        actual_distribution = output_dataframe['one'].value_counts(normalize=True).values
        # Expect the number of bins to saturate to the number of unique values instead of
        # creating a large number of empty bins between max and min values in the column
        unique_values_count = len(self.small_test_dataframe['one'].unique())
        expected_distribution = np.full(unique_values_count, 1 / unique_values_count)

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
            # Use pd.cut to bin the given column, then get normalized bin counts
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

        # Ensure the output rows are still assigned to the correct index value
        pd.testing.assert_frame_equal(
            input_dataframe.loc[output_dataframe.index],
            output_dataframe
        )

    def test_outliers_included_by_default(self):
        bin_count = 100
        test_dataframe_with_outlier = create_dataframe_with_one_outlier()

        unadjusted_samples = module.uniform(
            test_dataframe_with_outlier,
            columns_and_bin_counts={
                'one': bin_count
            }
        )

        # Expect the outlier to force max sample size to 1 sample per bin
        actual_samples_per_bin = len(unadjusted_samples) / bin_count
        assert actual_samples_per_bin == 1

    def test_outliers_ignored_with_quantile(self):
        bin_count = 100
        test_dataframe_with_outlier = create_dataframe_with_one_outlier()

        # Use bin_quantile parameter to ignore smallest sample bins
        outlier_adjusted_samples = module.uniform(
            test_dataframe_with_outlier,
            columns_and_bin_counts={
                'one': bin_count
            },
            bin_quantile=0.1
        )

        # Expect more than 1 sample / bin in the output
        actual_samples_per_bin = len(outlier_adjusted_samples) / bin_count
        assert actual_samples_per_bin > 1
