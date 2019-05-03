import numpy as np
from scipy.optimize import curve_fit

from osmo_jupyter.constants import IDEAL_GAS_CONSTANT_J_PER_MOL_K, DEGREES_CELSIUS_AT_ZERO_KELVIN


def _get_arrhenius_rate(temperature_c, preexponential_factor, activation_energy):
    ''' Estimate the temperature-dependent rate of a reaction using an Arrhenius equation
    https://en.wikipedia.org/wiki/Arrhenius_equation#Equation

    General form:
    k=A * e^(-Ea/RT)
    k is the rate "constant" (which is only truly constant at a given temperature)
    T is absolute temperature in kelvin
    A is preexponential factor (a constant)
    Ea is the activation energy
    R is the universal gas constant
    '''
    ideal_gas_constant = IDEAL_GAS_CONSTANT_J_PER_MOL_K
    temperature_kelvin = temperature_c + DEGREES_CELSIUS_AT_ZERO_KELVIN

    # Kinda silly, but this scales the activation energy to be more friendly to the regression.
    # Successful fits have had an activation energy around 10000.
    # Scaling in here allows the activation energy that the curve fitter knows about to be close to 1.
    activation_energy_scaling_factor = 10000
    exponent = -activation_energy * activation_energy_scaling_factor / (ideal_gas_constant * temperature_kelvin)

    return preexponential_factor * np.power(np.e, exponent)


def estimate_optical_reading_two_site_model_with_temperature(
        do_and_temp,
        f,
        A_i0,
        E_i0,
        A_k_sv1,
        A_k_sv2,
        E_k_sv
):
    ''' Two-site model fit including arrhenius equations for temperature dependence
    For more on the form of the equation, see:
    https://docs.google.com/document/d/1VDIn7b9xTZeuvdWRiF6P1HvRzde16HFVGKPHJrQfQGE/edit#heading=h.46ihesi06pxr

    The form is derived from:
    Lehner Eqn. 1.22 with Arrhenius temperature dependence of i0, k_sv1 and k_sv2
    as described by McNeil p.143 (though they do a more roundabout thing with β, it's equivalent)
    Note: Lehner and McNeil are predicting tau, we are predicting intensity (i)

    Args:
        do_and_temp: tuple of dissolved oxygen (% saturation) and temperature (Deg C)
        f: fraction of fluorophores in site 1 vs. site 2
            should always be less than 1.
        A_i0: Arrhenius preexponential parameter for unquenched fluorescence
        E_i0: Arrhenius activation energy (divided by 10000 for fit friendliness) for unquenched fluorescence
        A_k_sv1: Arrhenius preexponential parameter for stern-volmer fluorescence quenching model affected by oxygen
            in site 1
        A_k_sv2: Arrhenius preexponential parameter for stern-volmer fluorescence quenching model affected by oxygen
            in site 2
        E_k_sv: Arrhenius activation energy (divided by 10000 for fit friendliness) stern-volmer fluorescence
            quenching model
    Returns:
        estimate of a fluorescence reading
    '''

    do, temperature = do_and_temp

    i0 = _get_arrhenius_rate(temperature, A_i0, E_i0)
    k_sv1 = _get_arrhenius_rate(temperature, A_k_sv1, E_k_sv)
    k_sv2 = _get_arrhenius_rate(temperature, A_k_sv2, E_k_sv)

    return i0 * (f / (1 + k_sv1 * do) + (1 - f) / (1 + k_sv2 * do))


def estimate_do_two_site_model_with_temperature(
        optical_reading_and_temp,
        f,
        A_i0,
        E_i0,
        A_k_sv1,
        A_k_sv2,
        E_k_sv
):
    ''' Formula predicting DO based on optical reading and temperature
    This is the *reverse* of estimate_optical_reading_two_site_model_with_temperature.

    Args:
        optical_reading_and_temp: tuple of optical reading and temeprature (Deg C)
        f: fraction of fluorophores in site 1 vs. site 2
            should always be less than 1.
        A_i0: Arrhenius preexponential parameter for unquenched fluorescence
        E_i0: Arrhenius activation energy (divided by 10000 for fit friendliness) for unquenched fluorescence
        A_k_sv1: Arrhenius preexponential parameter for stern-volmer fluorescence quenching model affected by oxygen
            in site 1
        A_k_sv2: Arrhenius preexponential parameter for stern-volmer fluorescence quenching model affected by oxygen
            in site 2
        E_k_sv: Arrhenius activation energy (divided by 10000 for fit friendliness) stern-volmer fluorescence
            quenching model

    Returns:
        Estimate of dissolved oxygen
    '''

    optical_reading, temperature = optical_reading_and_temp
    i = optical_reading

    i0 = _get_arrhenius_rate(temperature, A_i0, E_i0)
    k_sv1 = _get_arrhenius_rate(temperature, A_k_sv1, E_k_sv)
    k_sv2 = _get_arrhenius_rate(temperature, A_k_sv2, E_k_sv)

    sqrt_term = (
        (i0 / i) ** 2 * (
            -2 * f * k_sv1 ** 2
            + f ** 2 * k_sv1 ** 2
            + f ** 2 * k_sv2 ** 2
            + 2 * f * k_sv1 * k_sv2
            - 2 * f ** 2 * k_sv1 * k_sv2
            + k_sv1 ** 2
        )
        + 2 * (i0 / i) * (
            f * k_sv1 ** 2
            - f * k_sv2 ** 2
            - k_sv1 ** 2
            + k_sv1 * k_sv2
        )
        + (
            k_sv1 ** 2
            + k_sv2 ** 2
            - 2 * k_sv1 * k_sv2
        )
    )
    # To prevent the regression falling into NaN-holes, prevent the square root term from going negative
    guarded_sqrt_term = np.abs(sqrt_term)

    up_front_terms = (i0 / i) * (k_sv1 - f * k_sv1 + f * k_sv2) - (k_sv1 + k_sv2)

    return (up_front_terms + np.sqrt(guarded_sqrt_term)) / (2 * k_sv1 * k_sv2)


# Fit parameters that have worked with various 2019-04 through 2019-05-02 calibration data sets
WORKING_FIT_PARAMS_DICT = {
    'f': 1.861e-01,
    'A_i0': 1.103e-01,
    'E_i0': -8.832e-01,
    'A_k_sv1': 1.683e-03,
    'A_k_sv2': 3.752e-02,
    'E_k_sv': -7.202e-02
}

WORKING_FIT_PARAMS = list(WORKING_FIT_PARAMS_DICT.values())


def get_optimal_DO_fit_params(
        training_data,
        estimate_do_fn=estimate_do_two_site_model_with_temperature,
        initial_fit_params=WORKING_FIT_PARAMS
):
    ''' Optimize fit parameters for a DO fit
    Args:
        training_data: DataFrame of observations with 'SR reading' and 'Temperature (C)' columns
        estimate_do_fn: function of ((optical reading, temperature), *fit params) which returns an estimate of DO % sat
        initial_fit_params: fit parameters to seed the curve fit. Pass None to skip initialization

    Returns:
        optimized fit parameters

    Raises:
        Various errors from scipy.optimize.curve_fit if a fit cannot be found.
    '''
    fit_params, pcov_dO = curve_fit(
        f=estimate_do_fn,
        xdata=np.array([training_data['SR reading'], training_data['Temperature (C)']]),
        ydata=training_data['DO (% sat)'],
        maxfev=10000,
        p0=initial_fit_params,
    )

    return fit_params
