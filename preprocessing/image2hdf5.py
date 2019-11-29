#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 15:40:02 2016

@author: pao
"""

from os.path import splitext

import matplotlib.pyplot as plt
import numpy as np
# %%
from PIL import Image

im_file = '../data/angry_test.jpg'
im_array = np.asarray(Image.open(im_file).convert('L'))
plt.imshow(im_array, cmap=plt.cm.Reds_r)
plt.show()

# %%

import h5py

nrows = im_array.shape[0]
ncols = im_array.shape[1]
ch_rows = 512
ch_cols = 512

h5_file = splitext(im_file)[0] + ".hdf5"

compression_filters = ["gzip", "lzf"]
compression = compression_filters[0]
shuffle_filter = [True, False]
shuffle = shuffle_filter[1]

file = h5py.File(h5_file, "w")
dset = file.create_dataset("adjacency", (nrows, ncols),
                           chunks=(ch_rows, ch_cols),
                           fillvalue=0,
                           compression=compression,
                           shuffle=shuffle,
                           dtype=np.int32)

dset[:] = im_array

file.flush()
file.close()
