import numpy as np
import plotly.graph_objs as go

from osmo_jupyter.constants import TEMPERATURE_STANDARD_OPERATING_MAX, TEMPERATURE_STANDARD_OPERATING_MIN, \
    DEGREES_CELSIUS_AT_ZERO_KELVIN, IDEAL_GAS_CONSTANT_J_PER_MOL_K, DO_PARTIAL_PRESSURE_MMHG_AT_1ATM
from osmo_jupyter.plot.color_from_temperature import color_from_temperature


def _get_rate_constant(temperature_c, preexponential_factor, activation_energy):
    ''' Estimate the rate constant for a reaction using an Arrhenius equation
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
    ''' This is a fit which worked pretty well with Ocean Optix patch data.
    It's a version of the two-site model which uses arrhenius equations for temperature dependence.
    Note that there are a lot of ways this could be tweaked.

    README for where this came from and with a lot of other useful info:
    https://docs.google.com/document/d/1lBv0aumCDdCd0JDt9hPw6aIExyhNtGtN9RVu_5sQ5yA/edit
    '''
    # First-pass fit params with ocean optics data using scipy.optimize.curve_fit.
    k_p_f = 7.818e-01
    k_p_i = 1.476e-02
    k_p_a = -1.725e+08  # Note: negative activation energy is not necessarily crazy.
    k_p_b = 2.094e+00
    activation_energy_i0 = -1.141e+00 * 10000
    activation_energy = 7.826e-01 * 10000

    # Original OO data had DO units in "percent of 760mmHg" or percent of 1atm.
    # Convert from percent saturation (% of 160mmHg)
    do_pct_of_760mmhg = do_pct_sat * DO_PARTIAL_PRESSURE_MMHG_AT_1ATM / 760

    # Assume activation energy is shared for all parameters except f, but the pre-exponential factor is different.
    i0 = _get_rate_constant(temperature_c, k_p_i, activation_energy_i0)
    ka = _get_rate_constant(temperature_c, k_p_a, activation_energy)
    kb = _get_rate_constant(temperature_c, k_p_b, activation_energy)
    f = _get_rate_constant(temperature_c, k_p_f, activation_energy)
    return i0 * f / (1 + ka * do_pct_of_760mmhg) + (1 - f) * i0 / (1 + kb * do_pct_of_760mmhg)


def get_optical_reading_normalized(do_pct_sat, temperature, min_value=0, max_value=1):
    ''' get an optical reading between a min and max value,
    with a DO and temperature relationship closely matching that seen in our patches in the past.

    This function also converts DO values to partial pressure to deal with the partial pressure unit used in the
    legacy fit.
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

    do_partial_pressure = do_pct_sat * 1.6

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
    ''' Quick plot of a single-patch optical reading over a range of temperatures and DO values. '''
    temperatures_to_plot = np.arange(TEMPERATURE_STANDARD_OPERATING_MIN, TEMPERATURE_STANDARD_OPERATING_MAX + 1, 5)
    do_domain = np.linspace(0, 100, 100)
    return go.FigureWidget(
        [
            go.Scatter(
                x=do_domain,
                y=get_optical_reading_normalized(do_domain, temperature),
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
            'title': 'Normalized optical reading from a patch',
            'xaxis': {'title': 'DO (% saturation)'},
            'yaxis': {'title': 'Optical reading (normalized max=1/min=0)'}
        }
    )
