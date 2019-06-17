import numpy as np
import plotly.graph_objs as go
import plotly.figure_factory as ff


def cut_array2d(array, block_shape):
    """ Cuts up an array into blocks of shape `block_shape`. If `block_shape` doesn't factor perfectly into the
        shape of the array, drops data from the right and bottom edges of the input `array`.
        Heavily, heavily adapted from https://stackoverflow.com/a/17385776/1701416

    Args:
        array: a 2D numpy array
        block_shape: a 2-tuple. The shape of the blocks you want the `array` to be cut into

    Return:
        (block_centers, blocks) tuple where
            block_centers: a 1D array of 2-tuple coordinates for the centers of the sliced blocks
            blocks: a 1D array of blocks of shape `block_shape`
    """
    array_height, array_width = array.shape
    block_height, block_width = block_shape

    # Think, gridlines:
    ycut = np.arange(0, array_height + 1, block_height)
    xcut = np.arange(0, array_width + 1, block_width)

    block_centers = [
        ((ycut[i] + ycut[i + 1] - 1) / 2, (xcut[j] + xcut[j + 1] - 1) / 2)
        for i, _ in enumerate(ycut[:-1])
        for j, _ in enumerate(xcut[:-1])
    ]

    blocks = [
        array[ycut[i] : ycut[i + 1], xcut[j] : xcut[j + 1]]
        for i, _ in enumerate(ycut[:-1])
        for j, _ in enumerate(xcut[:-1])
    ]

    return block_centers, blocks


def get_block_means_2d(block_centers, blocks, averaging_function=np.mean):
    """ Given 1D arrays of block_centers and blocks, construct a 2D array of block means.

    Args:
        block_centers: a 1D array of 2-tuple coordinates for the centers of the sliced blocks
        blocks: a 1D array of 2D blocks
        averaging_function: Optional (default=np.mean). Function to use to get the average of each block (a 2D array)

    Returns:
        a 2D array of block means
    """
    block_means = [averaging_function(block) for block in blocks]

    # block_centers is a list of (x,y) tuples: pixel coordinates of the blocks within the image
    # We don't actually care about the pixel coordinates - just the number of blocks in each row and column
    block_centers_x, block_centers_y = zip(*block_centers)
    blocks_height = len(set(block_centers_x))
    blocks_width = len(set(block_centers_y))

    # Construct a new 2D array that just contains the mean value of each block
    block_means_2d = np.reshape(block_means, newshape=(blocks_height, blocks_width))

    return block_means_2d


def display_heatmap(array, display_decimals=2, title="Heatmap"):
    """ Builds the heatmap figure from provided array

    Args:
        array: A 2D numpy array to render as a heatmap
        display_decimals: Optional (default=2). the number of decimals to round to in the annotation
        title: Optional (default='Heatmap')

    Returns:
        A heatmap Figure.
        Can be displayed in a jupyter notebook using the display() function.
    """
    heatmap = ff.create_annotated_heatmap(
        array, annotation_text=np.round(array, display_decimals)
    )

    heatmap.layout.yaxis.autorange = "reversed"
    heatmap.layout.title = title

    return go.FigureWidget(heatmap)


def heatmapify(
    array,
    averaging_function=np.mean,
    block_shape=(50, 50),
    display_decimals=2,
    title="Heatmap",
):
    """ Constructs a heatmap from a 2D array. The heatmap is created by slicing the array into blocks the size of
        `block_shape`, and then averaging each block.

    Args:
        array: A 2D numpy array to render as a heatmap. e.g. a single channel of an RGB image:
            array = image[:, :, channel]  # channel is 0, 1, or 2, for r, g, b respectively
        averaging_function: Optional (default=np.mean). Function to use to get the average of each block (a 2D array)
        block_shape: Optional (default=(50,50)). The shape of block to group by and average over to create the heatmap
        display_decimals: Optional (default=2). The number of decimals to round to in the annotation
        title: Optional (default='Heatmap').

    Returns:
        A heatmap Figure.
        Can be displayed in a jupyter notebook using the display() function.
    """
    block_centers, blocks = cut_array2d(array, block_shape)
    block_means_2d = get_block_means_2d(block_centers, blocks, averaging_function)

    return display_heatmap(block_means_2d, display_decimals, title)
