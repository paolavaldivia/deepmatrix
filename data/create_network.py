#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 16:53:09 2016

@author: pao
"""
import numpy as np
import h5py
import time

def barabasi_albert(A, number_of_nodes=1000, initial=5, average_degree=3):
    A[0:initial, 0:initial] = 1
    for i in range(initial):
        A[i,i] = 0
    nodes = list(range(initial))*(initial-1)
    for i in range(initial+1, number_of_nodes):
        perm = np.random.permutation(len(nodes))
        curr_deg = 0
        j = 0 

        while(curr_deg < average_degree):
            ind = perm[j]
            ni = nodes[ind]
            if A[i, ni] == 0 and i != ni:
                A[i, ni] = 1
                A[ni, i] = 1
                nodes.append(i)
                nodes.append(ni)
                curr_deg += 1
            j += 1
            

N = 2048
ch_nrows = 128
ch_ncols = 128

compression_filters = ["gzip", "lzf"]
compression = compression_filters[0]
shuffle_filter = [True, False]
shuffle = shuffle_filter[1]

file_name = "network_{}_{}-{}.hdf5".format(N, ch_nrows, ch_ncols)

file = h5py.File(file_name, "w")
dset = file.create_dataset("adjacency", (N, N), 
                        chunks=(ch_nrows, ch_ncols),
                        fillvalue=0,
                        compression=compression,
                        shuffle=shuffle)

st = time.time()
barabasi_albert(dset, number_of_nodes=N)
print('{:.2f}s'.format(time.time()-st))

file.close()