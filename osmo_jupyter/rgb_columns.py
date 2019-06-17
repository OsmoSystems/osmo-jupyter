from .constants import COLOR_CHANNELS


def _get_colors_with_pattern(pattern):
    """ Insert 'r', 'g', and 'b' into a given pattern, replacing the "*" in the pattern

    Args:
        pattern: string with an asterisk ("*") in place of the color letter, eg. '*_mean'
    Return:
        list of strings, with each color inserted into the pattern

    >>> _get_colors_with_pattern('*_mean')
    ['r_mean', 'g_mean', 'b_mean']
    """
    if "*" not in pattern:
        raise ValueError(f'Pattern "{pattern}" does not contain an asterisk ("*")')

    return [pattern.replace("*", color) for color in COLOR_CHANNELS]


def get_rgb_columns(df, pattern, other_columns_to_include=None):
    """ Get columns from the input DataFrame corresponding to colors, removing a shared prefix or suffix

    eg.
    >>> df = pd.DataFrame(..., columns=['r_mean', 'g_mean', 'b_mean', 'Timestamp', 'other', ...])
    >>> get_rgb_columns(df, '*_mean', ['Timestamp'])
    <DataFrame with columns ['r', 'g', 'b', 'Timestamp'] >

    Args:
        df: pandas.DataFrame of source data
        pattern: string with an asterisk ("*") in place of the color letter, eg. '*_mean'
        other_columns_to_include: list of column names to be included
    """
    other_columns_to_include = other_columns_to_include or []

    colors_with_pattern = _get_colors_with_pattern(pattern)

    all_desired_columns = colors_with_pattern + other_columns_to_include
    rename_map = {
        original_column: new_column
        for original_column, new_column in zip(colors_with_pattern, COLOR_CHANNELS)
    }
    return df[all_desired_columns].rename(columns=rename_map)


def add_rgb_columns(df_to_modify, rgb_df, pattern):
    """ Add rgb columns to a DataFrame (IN PLACE!) with a provided prefix or suffix pattern

    eg.
    >>> main_df = pd.DataFrame(..., columns=['Timestamp', ...])
    >>> rgb_means_df = pd.DataFrame(..., columns=['r', 'g', 'b'])
    >>> add_rgb_columns(main_df, rgb_means_df, '*_mean')
    >>> main_df
    <DataFrame with columns ['Timestamp', ..., 'r_mean', 'g_mean', 'b_mean'] >

    Args:
        df_to_modify: pandas.DataFrame to have columns added
        rgb_df: pandas.DataFrame with columns ['r', 'g', 'b'] to be added to df_to_modify
        pattern: string with an asterisk ("*") in place of the color letter, eg. '*_mean'
    Returns:
        None. df_to_modify will be altered in place.
    """
    colors_with_pattern = _get_colors_with_pattern(pattern)

    for color, color_in_pattern in zip(COLOR_CHANNELS, colors_with_pattern):
        df_to_modify[color_in_pattern] = rgb_df[color]
