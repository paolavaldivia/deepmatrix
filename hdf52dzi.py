import argparse
from os import path

import deepmatrix

SOURCE = "data/random.hdf5"
DZI_FILE = "data/random.dzi"

DATASET = 'adjacency'
IMAGE_OPTIONS = {'transparency': 0, 'compress_level': 0}  # {'quality': 100}
IMAGE_CREATOR_OPTIONS = {'tile_size': 512, 'tile_format': 'gif', 'image_mode': '1'}

def invert(data, dmax=1):
    return dmax - data



def create_deepzoom_images(source_file, dataset, dzi_file=None,
                           image_creator_options=None, image_options=None,
                           dmax=1):
    if dzi_file is None:
        dzi_file = path.splitext(source_file)[0] + ".dzi"

    if image_creator_options is None:
        image_creator_options = IMAGE_CREATOR_OPTIONS

    if image_options is None:
        image_options = IMAGE_OPTIONS

    creator = deepmatrix.ImageCreator(**image_creator_options,
                                      image_options=image_options,
                                      resize_filter="nearest")

    creator.create(source_file, dataset, dzi_file,
                   data_extent=[0, dmax])
    # data_op=invert)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='hdf5 dataset to deepzoom image converter.')
    parser.add_argument('--input', dest='source', type=str,
                        help='hdf5 file path')
    parser.add_argument('--output', dest='dzi_file', type=str,
                        default=None,
                        help='dzi_file output file path')
    parser.add_argument('--dataset', dest='dataset', type=str,
                        default=DATASET,
                        help='name of the dataset inside the hdf5 file')
    parser.add_argument('--tile_size', dest='tile_size', type=int,
                        default=IMAGE_CREATOR_OPTIONS['tile_size'],
                        help='tile size')
    parser.add_argument('--format', dest='tile_format', type=str,
                        default=IMAGE_CREATOR_OPTIONS['tile_format'],
                        help='tile format (gif, png, or any PIL supported format)')
    parser.add_argument('--mode', dest='image_mode', type=str,
                        default=IMAGE_CREATOR_OPTIONS['image_mode'],
                        help='image mode (1, L or any PIL supported mode)')
    parser.add_argument('--dmax', dest='dmax', type=int,
                        default=1,
                        help='dmax')

    args = parser.parse_args()

    print(args)

    image_options_ = IMAGE_OPTIONS
    image_creator_options_ = {'tile_size': args.tile_size, 'tile_format': args.tile_format, 'image_mode': args.image_mode}

    create_deepzoom_images(args.source, args.dataset, args.dzi_file,
                           image_creator_options=image_creator_options_,
                           image_options=image_options_, dmax=args.dmax)

    # creator = deepmatrix.ImageCreator(tile_size=args.tile_size, tile_format=args.tile_format,
    #                                   image_mode=args.image_mode, image_options=image_options_,
    #                                   resize_filter="nearest")
    #
    # dzi_file = args.dzi_file
    # if dzi_file is None:
    #     dzi_file = path.splitext(args.source)[0] + ".dzi"
    #
    # creator.create(args.source, args.dataset, dzi_file,
    #                data_extent=[0, 255])