import plotly.graph_objs as go


COLOR_CHANNELS = ['r', 'g', 'b']

# Axis # to use for each color when colors are being plotted on separate axes
AXES_BY_COLOR = {
    'r': 2,
    'g': 3,
    'b': 4,
}
ANNOTATION_AXIS = 1
SHARED_COLOR_AXIS = 2

AXIS_SIDES_BY_COLOR = {
    'r': 'left',
    'g': 'right',
    'b': 'right',
}

COLORS_BY_LETTER = {
    'r': 'red',
    'g': 'green',
    'b': 'blue'
}


def subsample_for_plot(df, dots_to_plot=150):
    ''' resample every nth row so that Plotting doesnt use so much CPU
    '''
    n = int(len(df) / dots_to_plot) or 1
    return df.iloc[::n, :]


def get_scatter(
    y_values,
    x_values=None,
    dataset_name=None,
    y_axis_number=1,
    marker_overrides=None,
    scatter_overrides=None,
):
    ''' Quick way to get a go.Scatter to put on your plot with some conveniences.

    Args:
        y_values: iterable of Y values can be a pandas Series or whatever
        x_values: Optional, X values to go along with those. If not provided, y_values is expected to be a Series and
            we'll use the index from it
        dataset_name: Optional, name to put in the chart legend. If not provided, y_values is expected to be a Series
            and we'll use its name
        y_axis_number: Optional, Y-axis number. Defaults to the primary (1) Y axis. Note that axes 2-4 are used for
            RGB values.
        marker_overrides: Optional, dict of go.Scatter.Marker attributes to override marker style.
            Valid options are documented at https://plot.ly/python/reference/#scatter-marker
        scatter_overrides: Optional, dict of go.Scatter attributes to override the Scatter.
            Valid options are documented at https://plot.ly/python/reference/#scatter
    '''
    x_column_values = x_values if x_values is not None else y_values.index
    name = dataset_name or y_values.name
    marker_overrides = marker_overrides or {}
    scatter_overrides = scatter_overrides or {}

    scatter_kwargs = dict(
        x=x_column_values,
        y=y_values,
        name=name,
        mode='markers',
        marker={
            'symbol': 'square',
            'size': 5,
            **marker_overrides
        },
        opacity=0.8,
        yaxis=f'y{y_axis_number}',
    )
    scatter_kwargs.update(scatter_overrides)
    return go.Scatter(
        **scatter_kwargs
    )


def get_rgb_scatters(
    rgb_df,
    x_column=None,
    colors_on_separate_axes=False,
    dataset_name=None,
    marker_overrides=None,
    scatter_overrides=None,
    colors_to_include=COLOR_CHANNELS,
):
    ''' get go.Scatter instances for each 'rgb' color in the input DataFrame

    example usage:
    >>> import pandas as  pd
    >>> import plotly.graph_objs as go
    >>> rgb_df = pd.DataFrame({'r': [1,2,3], 'g': [2,3,4], 'b': [3,4,5], 'x_axis': [0,1,2]})
    >>> go.FigureWidget(rgb_scatters(rgb_df, x_column='x_axis'))
    [result is a plot with your three channels]

    Args:
        rgb_df: pandas.DataFrame instance with 'r', 'g', and 'b' columns, and a column for the X axis value
        x_column: Optional, name of the column in rgb_df to use for the X axis values. if None, we'll use the index
        colors_on_separate_axes: Optional, if True, will plot each color series on a separate axis
        dataset_name: Optional, string to use in legend labels
        marker_overrides: Optional, dict of additional arguments for go.Marker.
            Valid options are documented at https://plot.ly/python/reference/#scatter-marker
        scatter_overrides: Optional, dict of additional_arguments for go.Scatter.
            Valid options are documented at https://plot.ly/python/reference/#scatter
        colors_to_include: Optional list of color letters to include - provide if you don't want all the colors.
            Should be a subset of COLOR_CHANNELS.
    Returns:
        list of go.Scatter objects, one each for r, g, and b or colors_to_include if provided
    '''
    marker_overrides = marker_overrides or {}
    x_column_values = rgb_df[x_column] if x_column else rgb_df.index
    return [
        get_scatter(
            x_values=x_column_values,
            y_values=rgb_df[color],
            dataset_name=f'{dataset_name} - {color}' if dataset_name is not None else color,
            marker_overrides={
                'color': COLORS_BY_LETTER[color],
                'symbol': 'circle-open',
                'size': 5,
                **marker_overrides
            },
            y_axis_number=AXES_BY_COLOR[color] if colors_on_separate_axes else SHARED_COLOR_AXIS,
            scatter_overrides=scatter_overrides,
        )
        for color in colors_to_include
    ]


def _axis_kwargs(axis_number, title, color=None, **y_axis_params):
    color_kwargs = {
        'titlefont': {'color': color},
        'tickfont': {'color': color},
        'tickcolor': color,
    } if color else {}
    return {
        f'yaxis{axis_number}': {
            'title': title,
            **color_kwargs,
            **y_axis_params
        }
    }


def _add_dicts(dicts):
    output_dict = {}
    for _dict in dicts:
        output_dict.update(_dict)
    return output_dict


def get_rgb_columns(df, pattern, other_columns_to_include=None):
    ''' Get columns from the input DataFrame corresponding to colors, removing a shared prefix or suffix

    eg.
    >>> df = pd.DataFrame(..., columns=['r_mean', 'g_mean', 'b_mean', 'Timestamp', 'other', ...])
    >>> get_rgb_columns(df, '*_mean', ['Timestamp'])
    <DataFrame with columns ['r', 'g', 'b', 'Timestamp'] >

    Args:
        df: pandas.DataFrame of source data
        pattern: string with an asterisk ("*") in place of the color letter, eg. '*_mean'
        other_columns_to_include: list of column names to be included
    '''
    other_columns_to_include = other_columns_to_include or []

    color_columns = [
        pattern.replace('*', color)
        for color in COLOR_CHANNELS
    ]

    all_desired_columns = color_columns + other_columns_to_include
    rename_map = {
        original_column: new_column
        for original_column, new_column in zip(color_columns, COLOR_CHANNELS)
    }
    return df[all_desired_columns].rename(columns=rename_map)


def get_layout_with_annotations(
    x_axis_title='Time',
    y_axis_title='',
    colors_on_separate_axes=False,
    events=None,
    **additional_layout_kwargs
):
    ''' Get a go.Layout instance prepared for our standard graphing needs

    Notes re. our standard layout:
    * The primary Y axis (y0) is reserved for annotations. This is done to guarantee that annotations show
    * If colors are on separate axes, they will be on the next consecutive axes, otherwise they will be on yaxis 2
    * You can use additional axes for plotting other things by passing in additional params

    Args:
        x_axis_title: title to use for X axis, default 'Time'
        y_axis_title: title to use for Y axis where colors are plotted. Required if colors_on_separate_axes is False.
            If colors_on_separate_axes is True, it will be used as a suffix for the y axis titles "r", "g", and "b"
        colors_on_separate_axes: whether colors (r,g and b) should be displayed on separate Y axes
        events: dictionary of {"annotation": x_axis_value} which will be used to annotate the chart
        additional_layout_kwargs: Any additional arguments will be passed to go.Layout. These can, for instance,
            be the result of _axis_kwargs() to add support for graphing more items.
            Valid options are documented at https://plot.ly/python/reference/#layout
    '''
    events = events or {}

    def get_color_y_axis_title(color):
        if not colors_on_separate_axes:
            return y_axis_title

        # blue and green are both on the right side, and applying a line break to blue lets them both be there
        # without overlapping
        line_break = '<br>' if color is 'b' else ''

        # If colors are on separate axes and a Y axis title is provided, use it as a suffix
        suffix = f' {y_axis_title}' if y_axis_title else ''
        return f'{line_break}{color}{suffix}'

    colors_on_separate_axes_kwargs = _add_dicts(
        _axis_kwargs(
            axis_number=AXES_BY_COLOR[color],
            color=COLORS_BY_LETTER[color],
            title=get_color_y_axis_title(color),
            overlaying='y',
            side=AXIS_SIDES_BY_COLOR[color],
        )
        for color in COLOR_CHANNELS
    )
    colors_on_same_axes_kwargs = _axis_kwargs(
        axis_number=SHARED_COLOR_AXIS,
        title=y_axis_title,
        overlaying='y',
        side='left',
    )
    color_y_axes = colors_on_separate_axes_kwargs if colors_on_separate_axes else colors_on_same_axes_kwargs

    # Prepare annotations & annotation axis

    # By default, the primary Y axis is invisible and used for annotations only,
    # but note that it can be overridden using additional_layout_kwargs
    primary_y_axis = {
        'yaxis': {
            'title': '',
            'visible': False,
        }
    }
    # We need to have at least 1 visible annotation on axis 1 or else plotted values will disappear
    # Note that this annotation is "visible" but doesn't have text or an arrow so it will not really be visible
    # https://github.com/plotly/plotly.py/issues/1200
    dummy_annotation = [{
        'yref': 'y',
        'xref': 'paper',
        'text': '',
        'showarrow': False,
        'visible': True,
    }]

    event_annotations = [
        {
            'x': x_value,
            'y': 0.95,
            'xref': 'x',
            'yref': 'paper',
            'text': title,
            'showarrow': True,
            'textangle': -55,
            'ax': 1
        }
        for title, x_value in events.items()
    ]

    # Combine these in dictionary form before passing them in to go.Layout so that conflicting keys can be resolved
    layout_kwargs = {
        'xaxis': {'title': x_axis_title},
        'annotations': event_annotations + dummy_annotation,
        **primary_y_axis,
        **color_y_axes,
        **additional_layout_kwargs
    }
    return go.Layout(**layout_kwargs)
