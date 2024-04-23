# imported from https://github.com/caethan/VolumeAnnotate/blob/main/main_app/loading.py (Brett Olsen)

import os
import zarr
import tifffile

def load_tifstack(path):
    """This function will take a path to a folder that contains a stack of .tif
    files and returns a concatenated 3D zarr array that will allow access to an
    arbitrary region of the stack.
    We support two different styles of .tif stacks.  The first are simply
    numbered filenames, e.g., 00.tif, 01.tif, 02.tif, etc.  In this case, the
    numbers are taken as the index into the zstack, and we assume that the zslices
    are fully continuous.
    The second follows @spelufo's reprocessing, and are not 2D images but 3D cells
    of the data.  These should be labeled
    cell_yxz_YINDEX_XINDEX_ZINDEX
    where these provide the position in the Y, X, and Z grid of cuboids that make
    up the image data.
    """
    # Get a list of .tif files
    tiffs = [filename for filename in os.listdir(path) if filename.endswith(".tif")]
    if all([filename[:-4].isnumeric() for filename in tiffs]):
        # This looks like a set of z-level images
        tiffs.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        paths = [os.path.join(path, filename) for filename in tiffs]
        store = tifffile.imread(paths, aszarr=True)
    elif all([filename.startswith("cell_yxz_") for filename in tiffs]):
        # This looks like a set of cell cuboid images
        images = tifffile.TiffSequence(os.path.join(path, "*.tif"), pattern=r"cell_yxz_(\d+)_(\d+)_(\d+)")
        store = images.aszarr(axestiled={0: 1, 1: 2, 2: 0})
    stack_array = zarr.open(store, mode="r")
    return stack_array