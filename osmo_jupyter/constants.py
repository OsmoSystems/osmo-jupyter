
# Science
IDEAL_GAS_CONSTANT_J_PER_MOL_K = 8.3144598  # J / (mol * K)
IDEAL_GAS_CONSTANT_L_ATM_PER_MOL_K = 0.08205  # (L * atm) / (mol * K)

DEGREES_CELSIUS_AT_ZERO_KELVIN = 273.15

# https://en.wikipedia.org/wiki/Atmosphere_(unit)
ONE_ATM_MMHG = 760.001

# https://www.wolframalpha.com/input/?i=fraction+of+oxygen+in+atmosphere
FRACTION_O2_IN_ATMOSPHERE = 0.20948

# Corresponds to 100% saturation at 1atm - use to convert between partial pressure and saturation
DO_PARTIAL_PRESSURE_MMHG_AT_1ATM = ONE_ATM_MMHG * FRACTION_O2_IN_ATMOSPHERE

# Full range of possible (in normal circumstances) DO partial pressures, in mmHg
DO_MIN_MMHG = 0
DO_MAX_MMHG = DO_PARTIAL_PRESSURE_MMHG_AT_1ATM

# Assume sea level, no salt, standard temp;
# details of how much this matters are discussed in 2019-02-18 updated DN error bounds
DO_SATURATION_AT_SEA_LEVEL_MG_PER_L = 8.26
STANDARD_MG_PER_L_PER_MMHG = DO_SATURATION_AT_SEA_LEVEL_MG_PER_L / DO_PARTIAL_PRESSURE_MMHG_AT_1ATM

# Error bounds
ERROR_BOUNDS_MG_PER_L = 0.3
ERROR_BOUNDS_MMHG = ERROR_BOUNDS_MG_PER_L / STANDARD_MG_PER_L_PER_MMHG

# Standard operating conditions
DO_STANDARD_OPERATING_MIN_MG_PER_L = 2
DO_STANDARD_OPERATING_MAX_MG_PER_L = 6
DO_STANDARD_OPERATING_MIN_MMHG = DO_STANDARD_OPERATING_MIN_MG_PER_L / STANDARD_MG_PER_L_PER_MMHG
DO_STANDARD_OPERATING_MAX_MMHG = DO_STANDARD_OPERATING_MAX_MG_PER_L / STANDARD_MG_PER_L_PER_MMHG

TEMPERATURE_STANDARD_OPERATING_MIN = 15
TEMPERATURE_STANDARD_OPERATING_MAX = 35

# RGB
COLOR_CHANNELS = ['r', 'g', 'b']

COLORS_BY_LETTER = {
    'r': 'red',
    'g': 'green',
    'b': 'blue'
}
