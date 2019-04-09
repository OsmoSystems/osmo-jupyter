import numpy as np
from plotly import graph_objs as go

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MAX, TEMPERATURE_STANDARD_OPERATING_MIN, \
    DO_MIN, DO_MAX


# These are functions to help plot simulations of DO, temperature, and optical reading


# Meshgrid and domain helpers
TEMPERATURE_DOMAIN = np.linspace(
    TEMPERATURE_STANDARD_OPERATING_MIN,
    TEMPERATURE_STANDARD_OPERATING_MAX,
    (TEMPERATURE_STANDARD_OPERATING_MAX-TEMPERATURE_STANDARD_OPERATING_MIN)+1
)
DO_DOMAIN = np.linspace(DO_MIN, DO_MAX, (DO_MAX - DO_MIN) + 1)

# In this notebook, we'll use a standard meshgrid of temperature and DO defined based on the domains above.
# Whenever you see a "meshgrid" passed around, it corresponds to these temperature and DO values.
# Use "indexing='ij'" to orient the meshgrids correctly so that dimension 0 iterates over DO
DO_MESHGRID, TEMPERATURE_MESHGRID = np.meshgrid(DO_DOMAIN, TEMPERATURE_DOMAIN, indexing='ij')


def get_meshgrid_of_do_and_temp(fn_of_do_and_temp):
    ''' Get values that correspond to the (global) DO and temperature meshgrids

    Params:
        fn_of_do_and_temp: Function which takes DO and temperature positional arguments (in that order)
    Returns:
        2d np.array of values from fn_of_do_and_temp
            dimension 0 will iterate over DO
            dimension 1 will iterate over temperatures
        this meshgrid will be appropriate to use on the Z axis of a plotly Surface
        where DO_MESHGRID is on the X axis and TEMPERATURE_MESHGRID is on the Y axis.
    '''
    return np.array([
        [
            fn_of_do_and_temp(do, temperature)
            for temperature in TEMPERATURE_DOMAIN
        ]
        for do in DO_DOMAIN
    ])


def plot_surface_of_do_and_temp(
    fn_or_meshgrid_of_do_and_temp,
    title,
    z_axis_title,
):
    ''' Create a surface plot of a DO- and temperature-dependent function.

    Args:
        fn_or_meshgrid_of_do_and_temp: either a function which takes DO saturation and temperature as positional
            arguments (in that order), OR a meshgrid corresponding to DO_MESHGRID and TEMPERATURE_MESHGRID.
            If callable, this function will be used with DO_MESHGRID and TEMPERATURE_MESHGRID to
            compute values at a standard range of temperature and DO values.
        title: title to use on the resulting chart
        z_axis_title: label for the Z axis - what does your function describe?
    Returns:
        plotly FigureWidget for your viewing pleasure
    '''
    # Accept either a pre-formed Z-axis meshgrid or a function that makes one
    z_meshgrid = (
        get_meshgrid_of_do_and_temp(fn_or_meshgrid_of_do_and_temp)
        if callable(fn_or_meshgrid_of_do_and_temp)
        else fn_or_meshgrid_of_do_and_temp
    )

    contour = {
        'show': True,
        'width': 1,
        'project': {
            'x': True,
            'y': True,
            'z': True
        }
    }

    return go.FigureWidget(
        [
            go.Surface(
                x=DO_MESHGRID,
                y=TEMPERATURE_MESHGRID,
                z=z_meshgrid,
                showscale=False,
                surfacecolor=TEMPERATURE_MESHGRID,
                opacity=0.9,
                contours=go.surface.Contours(
                    x=contour,
                    y=contour,
                    z=contour,
                )
            )
        ],
        layout={
            'title': title,
            'scene': {
                'xaxis': {'title': 'DO (% saturation)'},
                'yaxis': {'title': 'temperature (°C)'},
                'zaxis': {'title': z_axis_title},
            },
            'width': 700,
            'height': 700,
        }
    )
