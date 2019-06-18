import pandas as pd


def uniform(dataframe, columns_and_bin_counts, bin_quantile=0):
    '''
    Uniformly sample a DataFrame across n-dimensions.

    Args:
        dataframe: A pandas DataFrame
        columns_and_bin_counts: A dictionary of columns names and the number of bins
            over which to distribute each column
        bin_quantile: The lowest quantile of the combined bin sizes to use to determine
            the number of samples to take from each bin. Defaults to 0. Empty bins are ignored.

    Returns:
        A pandas DataFrame with a uniform distribution across the specified columns
    '''

    # Create bins for each requested columns
    binned = pd.DataFrame(
        {
            column: pd.cut(dataframe[column], bin_count)
            for column, bin_count in columns_and_bin_counts.items()
        },
    )

    # Combine all bins for each row into one series of n-dimensional bins
    combined_bins = binned.apply(tuple, axis=1)

    # Take samples from each bin
    samples_per_bin = combined_bins.value_counts().quantile(bin_quantile).astype(int)
    samples_index = combined_bins.groupby(
        combined_bins,
        group_keys=False
    ).apply(
        lambda bin_group:
            # Use min() to ensure sample doesn't throw in the event
            # samples_per_bin is larger than the number of samples possible
            bin_group.sample(min(samples_per_bin, len(bin_group)))
    ).index

    return dataframe.loc[samples_index]
