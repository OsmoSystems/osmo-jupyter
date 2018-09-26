
def to_max(dataframe):
    ''' Normalization method that finds the max value for each series and sets it to 1, dividing all other values
    accordingly.

    Useful for viewing curves on top of one another while also forcing them to have the same zero value (so that
    proportionality of changes is easy to find).

    Params:
        dataframe: pandas.DataFrame in which each column will be normalized
    Returns:
        new DataFrame with normalized columns
    '''
    return dataframe / dataframe.max()


def by_rgb_sum(rgb_df):
    ''' Normalize each series in the DataFrame by dividing by the sum of the r, g, and b values in each row

    Params:
        rgb_df: pandas.DataFrame instance with 'r', 'g', and 'b' columns
    Returns
        new DataFrame with all columns normalized by r+g+b
    '''
    normalization_series = rgb_df['r'] + rgb_df['g'] + rgb_df['b']
    return rgb_df.apply(lambda column: column / normalization_series, axis='rows')
