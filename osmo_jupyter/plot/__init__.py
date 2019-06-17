# Import from submodule to preserve backwards-compatibility with previous import paths.
# e.g. `from plot import get_scatter`

from .scatter import (
    get_rgb_scatters,
    get_scatter,
    get_layout_with_annotations,
)  # noqa: F401 unused imports
from .heatmap import heatmapify  # noqa: F401 unused imports


# Q: What code should live here?
# A: Anything that is directly related to displaying a plot in a jupyter notebook
