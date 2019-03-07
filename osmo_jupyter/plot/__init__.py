# Wildcard imports from each submodule preserve backwards-compatibility with previous import paths.
# e.g. `from plot import get_scatter`

from .layout import *  # noqa: F401, F403 unused wildcard imports
from .scatter import *  # noqa: F401, F403 unused wildcard imports
from .rgb_columns import *  # noqa: F401, F403 unused wildcard imports


# Q: What code should live here?
# A: Anything that is directly related to displaying a plot in a jupyter notebook

# Q: Then why is the rgb_columns.py module here?
# A: To preserve backwards compatibility, since it used to be in the ploy.py module
