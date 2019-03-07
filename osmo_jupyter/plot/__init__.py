# Wildcard imports from each submodule preserve backwards-compatibility with previous import paths.
# e.g. `from plot import get_scatter`

from .scatter import *  # noqa: F401, F403 unused wildcard imports


# Q: What code should live here?
# A: Anything that is directly related to displaying a plot in a jupyter notebook
