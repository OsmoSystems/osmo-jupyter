import inspect
from textwrap import dedent
from typing import List, Callable

from IPython.core.display import display
import numpy as np
import pandas as pd
from plotly import graph_objs as go

from osmo_jupyter.constants import (
    TEMPERATURE_STANDARD_OPERATING_MIN,
    TEMPERATURE_STANDARD_OPERATING_MAX,
)
from osmo_jupyter.plot.color_from_temperature import color_from_temperature
from osmo_jupyter.simulate.do_and_temp_meshgrid import DO_DOMAIN


def _get_r_squared(predicted, actual):
    """ Coefficient of determination (r-squared)

    Args:
        predicted: numpy array of Y data points provided by a model
        actual: numpy array of Y data points actually observed

    Returns:
        Coefficient of determination - a measure of how much of the variation in actual data
        is accounted for in the model
    """

    sum_of_squares_of_residuals = ((actual - predicted) ** 2).sum()
    total_sum_of_squares = ((actual - np.mean(actual)) ** 2).sum()

    return 1 - (sum_of_squares_of_residuals / total_sum_of_squares)


def _get_adjusted_r_squared(actual, predicted, p):
    """ Adjusted r-squared: Coefficient of determination adjusted for the number of explanatory variables in a model
    https://en.wikipedia.org/wiki/Coefficient_of_determination#Adjusted_R2

    Params:
        actual: actual values
        predicted: values predicted by a model, corresponding to actual values
        p: number of explanatory variables in the model
    Returns:
        adjusted r-squared value
    """
    n = len(actual)
    if n <= p + 1:
        raise ValueError(
            f"Number of data points {n} must be greater than the number of explanatory variables (p={p}) plus 1"
        )

    r_squared = _get_r_squared(actual, predicted)

    return 1 - (1 - r_squared) * (n - 1) / (n - p - 1)


def _get_fit_parameter_names(fn):
    """ Get the name of all but the first parameter to the given function """
    return list(inspect.signature(fn).parameters.keys())[1:]


def calibration_error_plot(predicted_do, actual_do, temperature, fit_title):
    """ Plot showing the error in predicted DO as distributed over DO and temperature """
    return go.FigureWidget(
        data=[
            go.Scatter(
                x=actual_do,
                y=predicted_do - actual_do,
                mode="markers",
                text=[f"T={T}" for T in temperature],
                marker=dict(
                    color=temperature,
                    symbol="circle-open",
                    colorscale="Bluered",
                    cmin=TEMPERATURE_STANDARD_OPERATING_MIN,
                    cmax=TEMPERATURE_STANDARD_OPERATING_MAX,
                ),
            )
        ],
        layout=go.Layout(
            title=f"DO error in {fit_title}",
            xaxis={"title": "Dissolved Oxygen (% saturation)", "range": [0, 100]},
            yaxis={"title": "DO error (predicted - actual)<br>(% saturation)"},
            hovermode="closest",
        ),
    )


def plot_calibration(
    sensor_data: pd.DataFrame,
    fit_params: List[float],
    title: str,
    estimate_do_fn: Callable,
    estimate_optical_reading_fn: Callable,
):
    """ Visualize sensor in the context of a curve fit and fit parameters, including numerical measures of fit quality.

    Args:
        sensor_data: pandas DataFrame of observations. should have the following columns:
            timestamp, Temperature (C), DO (% sat), SR reading
        fit_params: Fit parameters for the curve function connecting optical reading with DO and temperature
        title: Title of fit, to use in plots
        estimate_do_fn: Function of ((optical reading, temperature), *fit_params) which provides a DO estimate in % sat
        estimate_optical_reading_fn:
            Function of ((DO, temperature), *fit_params) which provides an optical reading estimate

    Returns:
        None. Produces plots and printed data frame
    """
    optical_reading = sensor_data["SR reading"]
    measured_do = sensor_data["DO (% sat)"]
    temperature = sensor_data["Temperature (C)"]

    predicted_do = estimate_do_fn((optical_reading, temperature), *fit_params)

    p = len(fit_params)
    adjusted_r_squared = _get_adjusted_r_squared(predicted_do, measured_do, p)

    fit_parameter_names = _get_fit_parameter_names(estimate_do_fn)
    fit_params_dict = dict(zip(fit_parameter_names, fit_params))
    fit_params_formatted = ", ".join(
        f"'{parameter_name}': {parameter_value:.3e}"
        for parameter_name, parameter_value in fit_params_dict.items()
    )

    # Estimate error
    do_error = predicted_do - measured_do
    max_do_error_index = do_error.abs().idxmax()
    max_do_error = do_error[max_do_error_index]
    worst_error_temperature = temperature[max_do_error_index]
    worst_error_correct_do = measured_do[max_do_error_index]
    worst_error_SR = optical_reading[max_do_error_index]

    temperatures_text = [f"T={T}" for T in temperature]
    print(
        dedent(
            f"""
    Fit params: {{ {fit_params_formatted} }}
    max DO prediction error:
        {max_do_error:.1f}% @ T={worst_error_temperature}, SR={worst_error_SR:.3f}, actual DO={worst_error_correct_do}
    standard deviation of DO error: {do_error.std():.1f}%
    DO error sum of squares: {(do_error ** 2).sum():.1f}
    adjusted r-squared (p={p}): {adjusted_r_squared:.4f}
    """
        )
    )

    calibration_and_prediction_traces = [
        go.Scatter(
            x=measured_do,
            y=optical_reading,
            mode="markers",
            name="Actual points",
            marker={
                "symbol": "circle-open",
                "size": 7,
                "color": sensor_data["Temperature (C)"],
                "colorscale": "Bluered",
            },
            text=temperatures_text,
            opacity=0.5,
        ),
        go.Scatter(
            x=predicted_do,
            y=optical_reading,
            mode="markers",
            name="Fit",
            marker={
                "symbol": "x",
                "color": sensor_data["Temperature (C)"],
                "colorscale": "Bluered",
            },
            text=temperatures_text,
        ),
    ]

    error_lines = [
        go.Scatter(
            x=[point_do, point_predicted_do],
            y=[point_optical_reading, point_optical_reading],
            line=dict(color="red", width=0.5, dash="dash"),
            text=[f"error: {point_predicted_do - point_do}"],
            mode="lines",
            showlegend=False,
            opacity=0.5,
        )
        for point_do, point_predicted_do, point_optical_reading, point_temperature in zip(
            measured_do, predicted_do, optical_reading, temperature
        )
    ]

    temperature_lines = [
        go.Scatter(
            x=DO_DOMAIN,
            y=estimate_optical_reading_fn((DO_DOMAIN, temperature), *fit_params),
            line=dict(color=color_from_temperature(temperature), width=0.5),
            name=f"fit @ T={temperature}",
            mode="lines",
        )
        for temperature in [15, 20, 25, 30, 35]
    ]

    display(
        go.FigureWidget(
            data=calibration_and_prediction_traces + error_lines + temperature_lines,
            layout=go.Layout(
                title=f"{title}",
                xaxis={"title": "Dissolved Oxygen (% saturation)"},
                yaxis={"title": "Spatial ratiometric reading"},
                hovermode="closest",
            ),
        )
    )

    display(calibration_error_plot(predicted_do, measured_do, temperature, title))
