import numpy as np
from plotly import graph_objs as go

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MAX, TEMPERATURE_STANDARD_OPERATING_MIN, \
    DO_MAX_MMHG, DO_MIN_MMHG


# These are surfaces of DO, temperature, and optical reading


# Meshgrid and domain helpers
TEMPERATURE_DOMAIN = np.linspace(
    TEMPERATURE_STANDARD_OPERATING_MIN,
    TEMPERATURE_STANDARD_OPERATING_MAX,
    (TEMPERATURE_STANDARD_OPERATING_MAX-TEMPERATURE_STANDARD_OPERATING_MIN)+1
)
n_do_domain_steps = np.int(np.round((DO_MAX_MMHG - DO_MIN_MMHG) + 1))
DO_DOMAIN = np.linspace(DO_MIN_MMHG, DO_MAX_MMHG, n_do_domain_steps)

# In this file, we'll use a standard meshgrid of temperature and DO defined based on the domains above.
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


def plot_meshgrid_of_do_and_temp_as_surface(meshgrid_of_do_and_temp, title, z_axis_title):
    ''' Create a surface plot of a DO- and temperature-dependent function.

    Args:
        meshgrid_of_do_and_temp: a meshgrid corresponding to DO_MESHGRID and TEMPERATURE_MESHGRID.
        title: title to use on the resulting chart
        z_axis_title: label for the Z axis - what does your function describe?
    Returns:
        plotly FigureWidget for your viewing pleasure
    '''
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
                z=meshgrid_of_do_and_temp,
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
                'xaxis': {'title': 'DO (mmHg)'},
                'yaxis': {'title': 'temperature (°C)'},
                'zaxis': {'title': z_axis_title},
            },
            'width': 700,
            'height': 700,
        }
    )


def plot_fn_of_do_and_temp_as_surface(fn_of_do_and_temp, title, z_axis_title):
    ''' Create a surface plot of a DO- and temperature-dependent function.

    Args:
        fn_of_do_and_temp: a function which takes DO partial pressure and temperature as positional arguments (in that
            order). This function will be used with DO_MESHGRID and TEMPERATURE_MESHGRID to compute values at a standard
            range of temperature and DO values.
        title: title to use on the resulting chart
        z_axis_title: label for the Z axis - what does your function describe?
    Returns:
        plotly FigureWidget for your viewing pleasure
    '''
    return plot_meshgrid_of_do_and_temp_as_surface(
        get_meshgrid_of_do_and_temp(fn_of_do_and_temp),
        title,
        z_axis_title
    )
