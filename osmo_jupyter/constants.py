
# Science
IDEAL_GAS_CONSTANT_J_PER_MOL_K = 8.314  # J / (mol * K)
IDEAL_GAS_CONSTANT_L_ATM_PER_MOL_K = 0.08205  # (L * atm) / (mol * K)

DEGREES_CELSIUS_AT_ZERO_KELVIN = 273.15

# Full range of possible DOs, in percent sat
DO_MIN = 0
DO_MAX = 100

# Corresponds to 100% saturation at 1atm - use to convert between partial pressure and saturation
DO_PARTIAL_PRESSURE_MMHG_AT_1ATM = 160

# Assume sea level, no salt, standard temp;
# details of how much this matters are discussed in 2019-02-18 updated DN error bounds
DO_SATURATION_AT_SEA_LEVEL_MG_PER_L = 8.26

# Standard operating conditions
DO_STANDARD_OPERATING_MIN_MG_PER_L = 2
DO_STANDARD_OPERATING_MAX_MG_PER_L = 6
DO_STANDARD_OPERATING_MIN = DO_STANDARD_OPERATING_MIN_MG_PER_L / DO_SATURATION_AT_SEA_LEVEL_MG_PER_L
DO_STANDARD_OPERATING_MAX = DO_STANDARD_OPERATING_MAX_MG_PER_L / DO_SATURATION_AT_SEA_LEVEL_MG_PER_L

TEMPERATURE_STANDARD_OPERATING_MIN = 15
TEMPERATURE_STANDARD_OPERATING_MAX = 35

# RGB
COLOR_CHANNELS = ['r', 'g', 'b']

COLORS_BY_LETTER = {
    'r': 'red',
    'g': 'green',
    'b': 'blue'
}
