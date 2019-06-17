import pandas as pd


def uniform(dataframe, columns_and_bin_counts):
    """
    Uniformly sample a DataFrame across n-dimensions.

    Args:
        dataframe: A pandas DataFrame
        columns_and_bin_counts: A dictionary of columns names and the number of bins
            over which to distribute each column

    Returns:
        A pandas DataFrame with a uniform distribution across the specified columns
    """

    # Create bins for each requested columns
    binned = pd.DataFrame(
        {
            column: pd.cut(dataframe[column], bin_count)
            for column, bin_count in columns_and_bin_counts.items()
        }
    )

    # Combine all bins for each row into one series of n-dimensional bins
    combined_bins = binned.apply(tuple, axis=1)

    # Take samples from each bin
    samples_per_bin = combined_bins.value_counts().min()
    samples_index = (
        combined_bins.groupby(combined_bins, group_keys=False)
        .apply(lambda bin_group: bin_group.sample(samples_per_bin))
        .index
    )

    return dataframe.loc[samples_index]
