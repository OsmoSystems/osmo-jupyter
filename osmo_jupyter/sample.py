import numpy as np
import pandas as pd


def uniform(dataframe, columns, bin_counts):
    '''
    Uniformly sample a DataFrame across n-dimensions.

    Args:
        dataframe: A pandas DataFrame
        columns: A list of columns names to sample uniformly
        bin_counts: A list of the number of bins over which to distribute each column
        Number of bins are assigned positionally to their respective column

    Returns:
        A pandas DataFrame with a uniform distribution across the specified columns
    '''

    # Create n-dimensional histogram of requested columns
    histogram = pd.DataFrame(
        [
            pd.cut(dataframe[columns[i]], bin_counts[i], labels=range(0, bin_counts[i]))
            for i in range(0, len(columns))
        ],
    ).transpose()
    histogram.index = dataframe.index.copy()
    # Combine all bins into one n-dimensional bin
    histogram['bin'] = pd.Categorical(histogram.apply(tuple, 1))

    max_samples = histogram['bin'].value_counts().min()
    samples = [
        histogram[histogram['bin'].astype(object) == bin].sample(max_samples).index.values
        for bin in histogram['bin'].unique()
    ]

    index = np.array(samples).flatten()
    return dataframe.loc[index]
