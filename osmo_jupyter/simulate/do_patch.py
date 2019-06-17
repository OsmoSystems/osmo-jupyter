import plotly.graph_objs as go

from osmo_jupyter.calibration.do.curve import estimate_optical_reading_two_site_model_with_temperature, \
    WORKING_FIT_PARAMS
from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MAX, TEMPERATURE_STANDARD_OPERATING_MIN, \
    DO_PARTIAL_PRESSURE_MMHG_AT_1ATM, DO_MAX
from osmo_jupyter.plot.color_from_temperature import color_from_temperature
from osmo_jupyter.simulate.do_and_temp_meshgrid import DO_DOMAIN, TEMPERATURE_DOMAIN


def _estimate_optical_reading(do_pct_sat, temperature_c):
    '''Estimate an optical reading given `do_pct_sat` and `temperature_c`, using a precalculated, hardcoded fit.
    '''
    return estimate_optical_reading_two_site_model_with_temperature(
        (do_pct_sat, temperature_c),
        *WORKING_FIT_PARAMS
    )


def get_optical_reading_normalized(do_pct_sat, temperature, min_value=0, max_value=1):
    '''Get a normalized optical reading between a min and max value, with DO and temperature relationship from a
    precalculated, hardcoded fit.

    Args:
        do_pct_sat: Dissolved Oxygen in percent saturation
        temperature: Temperature in degrees Celcius
        min_value: Optional (default=0). Minimum value for the normalized range
        max_value: Optional (default=1). Maximum value for the nomralized range

    Returns:
        An optical reading normalized to be within (optional) min_value and max_value.
    '''

    # Find minimum and maximum values to normalize with
    # Use DO range from 0 to 100, but temperature range from standard operating conditions
    # based on assumption: we still want to measure DO outside of SOC
    fit_optical_reading_min = _estimate_optical_reading(
        DO_PARTIAL_PRESSURE_MMHG_AT_1ATM,
        TEMPERATURE_STANDARD_OPERATING_MAX,
    )
    fit_optical_reading_max = _estimate_optical_reading(
        0,
        TEMPERATURE_STANDARD_OPERATING_MIN,
    )
    fit_optical_reading_range = fit_optical_reading_max - fit_optical_reading_min

    do_partial_pressure = do_pct_sat * DO_PARTIAL_PRESSURE_MMHG_AT_1ATM / DO_MAX

    fit_optical_reading = _estimate_optical_reading(
        do_partial_pressure,
        temperature,
    )

    normalized_optical_reading = (
            (fit_optical_reading - fit_optical_reading_min)
            / fit_optical_reading_range
    )
    range_ = max_value - min_value
    return normalized_optical_reading * range_ + min_value


def get_optical_reading_plot():
    '''Quick plot of a single-patch optical reading over a range of temperatures and DO values, using
    a precalculated, hardcoded fit.
    '''
    temperatures_to_plot = TEMPERATURE_DOMAIN[::5]

    return go.FigureWidget(
        [
            go.Scatter(
                x=DO_DOMAIN,
                y=get_optical_reading_normalized(DO_DOMAIN, temperature),
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
            'title': 'Normalized optical reading from a patch',
            'xaxis': {'title': 'DO (% saturation)'},
            'yaxis': {'title': 'Optical reading (normalized max=1/min=0)'}
        }
    )
