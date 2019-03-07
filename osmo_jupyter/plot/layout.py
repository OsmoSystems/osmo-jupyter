import plotly.graph_objs as go

from .constants import COLOR_CHANNELS, AXES_BY_COLOR, SHARED_COLOR_AXIS, COLORS_BY_LETTER


AXIS_SIDES_BY_COLOR = {
    'r': 'left',
    'g': 'right',
    'b': 'right',
}


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
        line_break = '<br>' if color == 'b' else ''

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
