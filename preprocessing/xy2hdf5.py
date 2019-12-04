import argparse
import time
import h5py
import numpy as np
from PIL import Image, ImageDraw
from os import path

import matplotlib.pyplot as plt

import scale

def scatter(xy, scale_x, scale_y, r=2, pixels=True):
    width = scale_x.get_range()[1] - scale_x.get_range()[0]
    height = scale_y.get_range()[1] - scale_y.get_range()[0]

    img = Image.new('1', (width, height))
    draw = ImageDraw.Draw(img)

    if len(xy) > 0:

        if type(xy) is list:
            xy = np.array(xy, ndmin=2)

        pos_sc = np.empty(xy.shape)

        pos_sc[:, 0] = scale_x(xy[:, 0])
        pos_sc[:, 1] = scale_y(xy[:, 1])

        if pixels:
            draw.point(list(pos_sc.flatten()), fill=1)
        else:
            for p in pos_sc:
                draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=255)

    return img


def extent(array):
    return np.min(array, axis=0), np.max(array, axis=0)


def create_scales(pos, width=512, height=512):
    min_, max_ = extent(pos)
    scale_x = scale.Scale(domain=(min_[0], max_[0]), rang=(0, width))
    scale_y = scale.Scale(domain=(min_[1], max_[1]), rang=(0, height))

    return scale_x, scale_y

def parse_dtype(dtype):
    if dtype == 'int':
        return np.int32
    if dtype == 'bool':
        return bool

def xy2hdf5(source_file, hdf5_file=None, size=1024, ch_size=512, dataset='xy',
            delimiter=' ', skiprows=0, dtype='int'):
    st = time.time()

    n_rows = size
    n_cols = size
    ch_rows = ch_size
    ch_cols = ch_size

    dtype = parse_dtype(dtype)

    xy = np.loadtxt(source_file, delimiter=delimiter, skiprows=skiprows)

    scale_x, scale_y = create_scales(xy, n_cols, n_rows)

    if hdf5_file is None:
        hdf5_file = path.splitext(source_file)[0] + ".hdf5"

    compression_filters = ["gzip", "lzf"]
    compression = compression_filters[0]
    shuffle_filter = [True, False]
    shuffle = shuffle_filter[1]

    file = h5py.File(hdf5_file, "w")
    h5_dataset = file.create_dataset(dataset, (n_rows, n_cols),
                               chunks=(ch_rows, ch_cols),
                               fillvalue=0,
                               compression=compression,
                               shuffle=shuffle,
                               dtype=dtype)

    img = scatter(xy, scale_x, scale_y)
    im_array = np.asarray(img, dtype=int)

    # plt.imshow(im_array, cmap=plt.cm.Reds_r)
    # plt.show()
    h5_dataset[:] = im_array

    print(np.sum(h5_dataset))

    file.flush()
    file.close()
    print('{:.2f}s'.format(time.time() - st))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='xy file projection to hdf5 matrix format')
    parser.add_argument('--input', dest='source', type=str, help='xy file path')
    parser.add_argument('--output', dest='hdf5_file', type=str,
                        default=None,
                        help='hdf5_file output file path')
    parser.add_argument('--size', dest='size', type=int,
                        default=1024,
                        help='resulting hdf5 file will be size x size')
    parser.add_argument('--chunk_size', dest='ch_size', type=int,
                        default=512,
                        help='chunk size')
    parser.add_argument('--dataset', dest='dataset', type=str,
                        default='xy',
                        help='name of the dataset inside the hdf5 file')
    parser.add_argument('--separator', dest='sep', type=str,
                        default=' ',
                        help='xy file sep')
    parser.add_argument('--skip_rows', dest='skip_rows', type=int,
                        default=0,
                        help='number of rows to skip')

    parser.add_argument('--dtype', dest='dtype', type=str,
                        default=0,
                        help='dtype')

    args = parser.parse_args()

    xy2hdf5(args.source, args.hdf5_file, args.size, args.ch_size,
            args.dataset,  args.sep, args.skip_rows, args.dtype)
