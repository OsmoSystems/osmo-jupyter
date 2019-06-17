from osmo_jupyter.constants import (
    TEMPERATURE_STANDARD_OPERATING_MAX,
    TEMPERATURE_STANDARD_OPERATING_MIN,
)


def color_from_temperature(temperature):
    """ Basic color scale going from blue at the minimum temperature to red at the max temperature.
    Note: this corresponds to the behavior of the Bluered color scale implemented by plotly - when setting marker
        color, use that instead. This can be used for line color.
    """
    temp_range = TEMPERATURE_STANDARD_OPERATING_MAX - TEMPERATURE_STANDARD_OPERATING_MIN
    temp_as_fraction = (temperature - TEMPERATURE_STANDARD_OPERATING_MIN) / temp_range

    r = int(temp_as_fraction * 255)
    b = int((1 - temp_as_fraction) * 255)

    return f"rgb({r}, 0, {b})"
