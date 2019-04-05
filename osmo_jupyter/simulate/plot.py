import numpy as np
from plotly import graph_objs as go

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MAX, TEMPERATURE_STANDARD_OPERATING_MIN


# Meshgrid and domain helpers
TEMPERATURE_DOMAIN = np.linspace(TEMPERATURE_STANDARD_OPERATING_MIN, TEMPERATURE_STANDARD_OPERATING_MAX, (TEMPERATURE_STANDARD_OPERATING_MAX-TEMPERATURE_STANDARD_OPERATING_MIN)*2+1)
# Something weird happens at exactly 0 DO with the 2-site model fit on OO data. Skip 0 DO and go to 1
DO_DOMAIN = np.linspace(0, 100, 201)

# In this notebook, we'll use a standard do-vs-temp meshgrid defined based on the domains above.
# Whenever you see a "meshgrid" passed around, it corresponds to these temperature and DO values.
DO_MESHGRID, TEMPERATURE_MESHGRID = np.meshgrid(DO_DOMAIN, TEMPERATURE_DOMAIN)


def get_meshgrid(fn_of_do_and_temp):
    ''' Get values that correspond to the DO and temperature meshgrids

    Params:
        fn_of_do_and_temp: Function which takes DO and temperature positional arguments
    Returns:
        2d np.array of values from fn_of_do_and_temp
            dimension 0 will iterate over temperatures
            dimension 1 will iterate over DO
        this meshgrid will be appropriate to use on the Z axis of a plotly Surface
        where TEMPERATURE_MESHGRID is on the X axis and DO_MESHGRID is on the Y axis.
    '''
    return np.array([
        [
            fn_of_do_and_temp(do, temperature)
            for do in DO_DOMAIN
        ]
        for temperature in TEMPERATURE_DOMAIN
    ])


def plot_do_temp_surface(
    fn_or_meshgrid_of_do_and_temp,
    title,
    z_axis_title,
):
    ''' Create a surface plot of a DO- and temperature-dependent function.

    Args:
        fn_or_meshgrid_of_do_and_temp: either a function which takes DO saturation and temperature
            as positional arguments (in that order),
            or a meshgrid corresponding to DO_MESHGRID and TEMPERATURE_MESHGRID.
            If callable, this function will be used with DO_MESHGRID and TEMPERATURE_MESHGRID to
            compute values at a standard range of temperature and DO values.
        title: title to use on the resulting chart
        z_axis_title: label for the Z axis - what does your function describe?
    Returns:
        plotly FigureWidget for your viewing pleasure
    '''
    # Accept either a pre-formed Z-axis meshgrid or a function that makes one
    z_meshgrid = (
        get_meshgrid(fn_or_meshgrid_of_do_and_temp)
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
                x=TEMPERATURE_MESHGRID,
                y=DO_MESHGRID,
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
                'xaxis': {'title': 'temperature (°C)'},
                'yaxis': {'title': 'DO (% saturation)'},
                'zaxis': {'title': z_axis_title},
            },
            'width': 700,
            'height': 700,
        }
    )
