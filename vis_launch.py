import linecache
import argparse
import ast
import numpy as np
from mayavi import mlab
from functools import partial

SLICE_VARIANTS = [
    'x', 'y', 'z',
    'xx', 'xy', 'xz',
    'yx', 'yy', 'yz',
    'zx', 'zy', 'zz',
    'xs', 'ys', 'zs'
]
DESCRIPTION = """
Tool for setting up and launching a Mayavi visualization.
Defaults to quiver plot(if no optional arguments are present).
Aditional arguments hide quiver plot.
"""
SLICE_DESCRIPTION = """
Add a slice. Multiple slices can be added by repeating the argument.
The format is two letters, where the first letter is the axis of slice.
Second letter is the vector component to visualize. 's' is the scalar 
size of the vector. If the second character is omited, the slice is 
a vector field slice. EXAMPLE: "-s xy -s x -s zx"
"""

def split_further(input_array, size):
    array = []
    for item in input_array:
        array.append(np.split(item, size))
    return np.array(array)


def load_data(input_file):
    # read and parse the metadata
    metadata = ast.literal_eval(linecache.getline(input_file, 2))

    # load the .csv values
    x, y, z, u, v, w = np.loadtxt(input_file, delimiter=', ', skiprows=3, unpack=True)
    
    # split the data
    # currently expects that the data and easily splitable in linear way and does not need reordering
    x_new = np.split(u, metadata['steps'][2])
    y_new = np.split(v, metadata['steps'][2])
    z_new = np.split(w, metadata['steps'][2])

    # we need to swap axes to properly rotate the data as the splitting inverts along one axis
    x_new = np.swapaxes(split_further(x_new, metadata['steps'][1]), 0, 2)
    y_new = np.swapaxes(split_further(y_new, metadata['steps'][1]), 0, 2)
    z_new = np.swapaxes(split_further(z_new, metadata['steps'][1]), 0, 2)
    return x_new, y_new, z_new


def main(args):
    # load the data and prepare the Mayavi pipeline sources
    x, y, z = load_data(args["DATAFILE"])
    vec_src = mlab.pipeline.vector_field(x, y, z)
    mag_src = mlab.pipeline.extract_vector_norm(vec_src)
    x_src = mlab.pipeline.scalar_field(x)
    y_src = mlab.pipeline.scalar_field(y)
    z_src = mlab.pipeline.scalar_field(z)
    
    draw_vectors = True

    # pre-prepare the various slices we can do, as a partial function to call
    slice_dict = {
        'x': partial(mlab.pipeline.vector_cut_plane, vec_src, plane_orientation='x_axes'),
        'y': partial(mlab.pipeline.vector_cut_plane, vec_src, plane_orientation='y_axes'),
        'z': partial(mlab.pipeline.vector_cut_plane, vec_src, plane_orientation='z_axes'),
        'xx': partial(mlab.pipeline.scalar_cut_plane, x_src, plane_orientation='x_axes'),
        'xy': partial(mlab.pipeline.scalar_cut_plane, y_src, plane_orientation='x_axes'),
        'xz': partial(mlab.pipeline.scalar_cut_plane, z_src, plane_orientation='x_axes'),
        'yx': partial(mlab.pipeline.scalar_cut_plane, x_src, plane_orientation='y_axes'),
        'yy': partial(mlab.pipeline.scalar_cut_plane, y_src, plane_orientation='y_axes'),
        'yz': partial(mlab.pipeline.scalar_cut_plane, z_src, plane_orientation='y_axes'),
        'zx': partial(mlab.pipeline.scalar_cut_plane, x_src, plane_orientation='z_axes'),
        'zy': partial(mlab.pipeline.scalar_cut_plane, y_src, plane_orientation='z_axes'),
        'zz': partial(mlab.pipeline.scalar_cut_plane, z_src, plane_orientation='z_axes'),
        'xs': partial(mlab.pipeline.scalar_cut_plane, mag_src, plane_orientation='x_axes'),
        'ys': partial(mlab.pipeline.scalar_cut_plane, mag_src, plane_orientation='y_axes'),
        'zs': partial(mlab.pipeline.scalar_cut_plane, mag_src, plane_orientation='z_axes')
    }

    # add the various visualizations
    if args["slice"] is not None:
        draw_vectors = False
        for item in args["slice"]:
            slice_dict[item]()
    
    if args["isosurf"] is not None:
        draw_vectors = False
        mlab.pipeline.iso_surface(mag_src, contours=args["isosurf"], opacity=0.4)

    if args["fieldlines"]:
        draw_vectors = False
        mlab.pipeline.streamline(mag_src, integration_direction='both', 
                                 seed_resolution=15, seed_scale=1, seedtype='plane')
    
    if draw_vectors or args["vectors"]:
        mlab.pipeline.vectors(vec_src)
    
    mlab.show()



if __name__ == "__main__":
    # cmd argument parsing and help
    parser = argparse.ArgumentParser(
            description = DESCRIPTION,
            allow_abbrev=False,
            usage="vis_launch.py DATAFILE [-v] [-f] [-s SLICE] [-i NUM] [-h]"
    )
    parser.add_argument('DATAFILE',
           help="Input file in .csv format containing the source data for visualization.")
    parser.add_argument('-f', '--fieldlines', action='store_true',
           help="Toggle fieldlines.")
    parser.add_argument('-v', '--vectors', action='store_true',
           help="Force the rendering of quiver plot.")
    parser.add_argument('-i', '--isosurf', type=int, const=5, nargs='?', metavar='NUM',
           help="Toggle isosurfaces. Defaults to 5 levels if NUM is not specified.")
    parser.add_argument('-s' , '--slice', action='append', choices=SLICE_VARIANTS, metavar='SLICE',
           help=SLICE_DESCRIPTION)
    parser.add_argument('--version',
           action = 'version',
           version = '%(prog)s 0.1'
    )
    arguments = vars(parser.parse_args())
    main(arguments)
