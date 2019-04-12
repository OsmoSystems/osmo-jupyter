import numpy as np
import plotly.graph_objs as go

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MAX, TEMPERATURE_STANDARD_OPERATING_MIN, \
    DEGREES_CELSIUS_AT_ZERO_KELVIN, IDEAL_GAS_CONSTANT_J_PER_MOL_K, DO_PARTIAL_PRESSURE_MMHG_AT_1ATM, DO_MAX
from osmo_jupyter.plot.color_from_temperature import color_from_temperature
from osmo_jupyter.simulate.do_and_temp_meshgrid import DO_DOMAIN, TEMPERATURE_DOMAIN


FIT_SOURCE_DOCUMENTATION = '''
---
Details about the optical reading fit and source data:
    Source data: Ocean Optics patch data.

    Fit type: a version of the two-site model which uses arrhenius equations for temperature dependence.
    (Note that there are a lot of ways this could be tweaked.)

    As part of this, we convert DO values to partial pressure to match the partial pressure unit used in the
    legacy fit.

    README for where this came from and with a lot of other useful info:
    https://docs.google.com/document/d/1lBv0aumCDdCd0JDt9hPw6aIExyhNtGtN9RVu_5sQ5yA/edit
'''


def _get_rate_constant(temperature_c, preexponential_factor, activation_energy):
    '''Estimate the rate constant for a reaction using an Arrhenius equation
    https://en.wikipedia.org/wiki/Arrhenius_equation#Equation

    General form:
    k=A * e^(-Ea/RT)
    k is the rate constant
    T is absolute temperature in kelvin
    A is preexponential factor (a constant)
    Ea is the activation energy
    R is the ideal gas constant
    '''
    temperature_kelvin = temperature_c + DEGREES_CELSIUS_AT_ZERO_KELVIN
    exponent = -activation_energy / (IDEAL_GAS_CONSTANT_J_PER_MOL_K * temperature_kelvin)
    return preexponential_factor * np.power(np.e, exponent)


def _estimate_optical_reading(do_pct_sat, temperature_c):
    '''Estimate an optical reading given `do_pct_sat` and `temperature_c`, using a precalculated, hardcoded fit.
    '''
    # First-pass fit params with ocean optics data using scipy.optimize.curve_fit.
    k_p_f = 7.818e-01
    k_p_i = 1.476e-02
    k_p_a = -1.725e+08  # Note: negative activation energy is not necessarily crazy.
    k_p_b = 2.094e+00
    activation_energy_i0 = -1.141e+04
    activation_energy = 7.826e+03

    # Original OO data had DO units in "percent of 760mmHg" or percent of 1atm.
    # Convert from percent saturation (% of 160mmHg)
    do_pct_of_760mmhg = do_pct_sat * DO_PARTIAL_PRESSURE_MMHG_AT_1ATM / 760

    # Assume activation energy is shared for all parameters except f, but the pre-exponential factor is different.
    i0 = _get_rate_constant(temperature_c, k_p_i, activation_energy_i0)
    ka = _get_rate_constant(temperature_c, k_p_a, activation_energy)
    kb = _get_rate_constant(temperature_c, k_p_b, activation_energy)
    f = _get_rate_constant(temperature_c, k_p_f, activation_energy)
    return i0 * f / (1 + ka * do_pct_of_760mmhg) + (1 - f) * i0 / (1 + kb * do_pct_of_760mmhg)


# Dynamically update the __doc__ to include the FIT_SOURCE_DOCUMENTATION
_estimate_optical_reading.__doc__ += FIT_SOURCE_DOCUMENTATION


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


# Dynamically update the __doc__ to include the FIT_SOURCE_DOCUMENTATION
get_optical_reading_normalized.__doc__ += FIT_SOURCE_DOCUMENTATION


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


# Dynamically update the __doc__ to include the FIT_SOURCE_DOCUMENTATION
get_optical_reading_plot.__doc__ += FIT_SOURCE_DOCUMENTATION
