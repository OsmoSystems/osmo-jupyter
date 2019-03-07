import plotly.graph_objs as go

from .constants import COLOR_CHANNELS, AXES_BY_COLOR, SHARED_COLOR_AXIS, COLORS_BY_LETTER


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
