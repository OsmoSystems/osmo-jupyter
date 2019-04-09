import plotly.graph_objs as go

from osmo_jupyter.plot.color_from_temperature import color_from_temperature
from osmo_jupyter.simulate.do_patch import get_optical_reading_normalized
from osmo_jupyter.simulate.do_and_temp_plot import DO_DOMAIN, TEMPERATURE_DOMAIN


def simulate_spatial_ratiometric_reading(
    do,
    temperature,
    sealed_patch_do=0,
    sealed_patch_kwargs={},
    unsealed_patch_kwargs={}
):
    ''' Simulate a "spatial ratiometric" reading using a sealed DO patch as the ratiometric reference

    Args:
        do: Dissolved Oxygen in percent saturation in the unsealed patch
        temperature: Temperature in degrees Celcius
        sealed_patch_do: Optional (default=0). Dissolved Oxygen in percent saturation in the sealed patch
        sealed_patch_kwargs: Optional. Additional args passed to get_optical_reading_normalized for the sealed patch
        unsealed_patch_kwargs: Optional. Additional args passed to get_optical_reading_normalized for the unsealed patch

    Returns:
        An optical reading normalized to be within (optional) min_value and max_value.
    '''

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
    temperatures_to_plot = TEMPERATURE_DOMAIN[::5]

    return go.FigureWidget(
        [
            go.Scatter(
                x=DO_DOMAIN,
                y=simulate_spatial_ratiometric_reading(DO_DOMAIN, temperature),
                mode='lines',
                line={
                    'color': color_from_temperature(temperature),
                    'width': 1,
                },
                name=f'T={temperature}',
            )
            for temperature in temperatures_to_plot
        ],
        layout={
            'title': 'spatial ratiometric reading over DO and temperature',
            'xaxis': {'title': 'DO (% saturation)'},
            'yaxis': {'title': 'Spatial Ratiometric Reading (unitless)'}
        }
    )
