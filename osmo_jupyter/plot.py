import plotly.graph_objs as go


COLOR_CHANNELS = ['r', 'g', 'b']

# Axis # to use for each color when colors are being plotted on separate axes
AXES_BY_COLOR = {
    'r': 2,
    'g': 3,
    'b': 4,
}
ANNOTATION_AXIS = 1
NON_ANNOTATION_AXIS = 2


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


def get_rgb_scatters(
    rgb_df,
    x_column=None,
    colors_on_separate_axes=False,
    dataset_name=None,
    marker_overrides=None,
    colors_to_include=COLOR_CHANNELS,
):
    ''' get go.Scatter instances for each 'rgb' color in the input DataFrame

    example usage:
    >>> import pandas as  pd
    >>> import plotly.graph_objs as go
    >>> rgb_df = pd.DataFrame({'r': [1,2,3], 'g': [2,3,4], 'b': [3,4,5], 'x_axis': [0,1,2]})
    >>> go.FigureWidget(rgb_scatters(rgb_df, x_column='x_axis'))
    [result is a plot with your three channels]

    Params:
        rgb_df: pandas.DataFrame instance with 'r', 'g', and 'b' columns, and a column for the X axis value
        x_column: Optional, name of the column in rgb_df to use for the X axis values. if None, we'll use the index
        colors_on_separate_axes: Optional, if True, will plot each color series on a separate axis
        dataset_name: Optional, string to use in legend labels
        marker_overrides: Optional, dict of additional arguments
        colors_to_include: Optional list of color letters to include - provide if you don't want all the colors.
            Should be a subset of COLOR_CHANNELS.
    Returns:
        list of go.Scatter objects, one each for r, g, and b or colors_to_include if provided
    '''
    marker_overrides = marker_overrides or {}
    x_column_values = rgb_df[x_column] if x_column else rgb_df.index
    return [
        go.Scatter(
            x=x_column_values,
            y=list(rgb_df[color]),
            name=f'{dataset_name} - {color}' if dataset_name is not None else color,
            mode='markers',
            marker={
                'color': COLORS_BY_LETTER[color],
                'symbol': 'circle-open',
                'size': 5,
                **marker_overrides
            },
            opacity=0.8,
            # yaxis='y3',
            yaxis=f'y{AXES_BY_COLOR[color]}' if colors_on_separate_axes else f'y{NON_ANNOTATION_AXIS}'
        )
        for color in colors_to_include
    ]


def axis_kwargs(axis_number, title, color=None, **y_axis_params):
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

    Params:
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
    y_axis_title=None,
    colors_on_separate_axes=False,
    events=None,
    **additional_layout_params
):
    ''' Get a go.Layout instance prepared for our standard graphing needs

    Notes re. our standard layout:
    * The primary Y axis (y0) is reserved for annotations. This is done to guarantee that annotations show
    * If colors are on separate axes, they will be on the next consecutive axes, otherwise they will be on yaxis 2
    * You can use additional axes for plotting other things by passing in additional params

    Params:
        x_axis_title: title to use for X axis, default 'Time'
        y_axis_title: title to use for Y axis where colors are plotted. Required if colors_on_separate_axes is False.
            If colors_on_separate_axes is True, it will be used as a suffix for the y axis titles "r", "g", and "b"
        colors_on_separate_axes: whether colors (r,g and b) should be displayed on separate Y axes
        events: dictionary of {x_axis_value: "annotation"} which will be used to annotate the chart
        additional_layout_params: These will be passed to go.Layout. These can, for instance, be the result of
            axis_kwargs() to add support for graphing more items.
    '''
    events = events or {}
    if not colors_on_separate_axes and not y_axis_title:
        raise ValueError('If colors_on_separate_axes is False you must provide a y_axis_title')

    annotation_y_axis = {
        'yaxis': {
            'title': '',
            'range': [0, 1],
            'visible': False,
        }
    }

    def get_color_y_axis_title(color):
        if not colors_on_separate_axes:
            return y_axis_title

        # "blue" axis uses a line break to not overlap unnecessarily with green
        line_break = '<br>' if color == 'b' else ''

        # If colors are on separate axes and a Y axis title is provided, use it as a suffix
        suffix = f' {y_axis_title}' if y_axis_title else ''
        return f'{line_break}{color}{suffix}'

    color_y_axes = _add_dicts(
        axis_kwargs(
            axis_number=AXES_BY_COLOR[color],
            color=COLORS_BY_LETTER[color],
            title=get_color_y_axis_title(color),
            overlaying='y',
            side='left' if AXES_BY_COLOR[color] <= 2 else 'right',
            # visible=True,  # TODO AXES_BY_COLOR[color] <= 3,
        )
        for color in COLOR_CHANNELS
    ) if colors_on_separate_axes else axis_kwargs(
        axis_number=NON_ANNOTATION_AXIS,
        title=y_axis_title,
        overlaying='y',
        side='left',
    )

    # We need to have at least 1 annotation on axis 1 or else plotted values will disappear
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
            'yref': 'y',
            'text': title,
            'showarrow': True,
            'textangle': -55,
            'ax': 1
        }
        for title, x_value in events.items()
    ]

    return go.Layout(
        xaxis={'title': 'Time'},
        annotations=dummy_annotation + event_annotations,
        **annotation_y_axis,
        **color_y_axes,
        **additional_layout_params
    )
