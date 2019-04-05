import numpy as np
import plotly.graph_objs as go

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MIN, TEMPERATURE_STANDARD_OPERATING_MAX

from osmo_jupyter.plot.color_from_temperature import color_from_temperature
from osmo_jupyter.simulate.do_patch import get_optical_reading_normalized


def simulate_spatial_ratiometric_reading(
    do,
    temperature,
    sealed_patch_do=0,
    sealed_patch_kwargs={},
    unsealed_patch_kwargs={}
):
    unsealed_patch_reading = get_optical_reading_normalized(
        do,
        temperature,
        **unsealed_patch_kwargs,
    )
    sealed_patch_reading = get_optical_reading_normalized(
        sealed_patch_do,
        temperature,
        **sealed_patch_kwargs
    )
    return unsealed_patch_reading / sealed_patch_reading


def get_ratiometric_reading_plot():
    ''' Quick plot of a spatial ratiometric optical reading over a range of temperatures and DO values. '''
    temperatures_to_plot = np.arange(TEMPERATURE_STANDARD_OPERATING_MIN, TEMPERATURE_STANDARD_OPERATING_MAX + 1, 5)
    do_domain = np.linspace(0, 100, 100)
    return go.FigureWidget(
        [
            go.Scatter(
                x=do_domain,
                y=simulate_spatial_ratiometric_reading(do_domain, temperature),
                mode='lines',
                line={
                    'color': color_from_temperature(temperature),
                    'width': 1,
                },
                name=f'T={temperature:d}',
            )
            for temperature in temperatures_to_plot
        ],
        layout={
            'title': 'spatial ratiometric reading over DO and temperature',
            'xaxis': {'title': 'DO (% saturation)'},
            'yaxis': {'title': 'Spatial Ratiometric Reading (unitless)'}
        }
    )
