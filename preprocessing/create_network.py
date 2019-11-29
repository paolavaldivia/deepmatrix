#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 16:53:09 2016

@author: pao
"""
import time

import h5py
import numpy as np
from scipy import sparse


def barabasi_albert(A, initial=5, average_degree=3):
    number_of_nodes = A.shape[0]  # assuming A is square
    A[0:initial, 0:initial] = 1
    for i in range(initial):
        A[i, i] = 0
    nodes = list(range(initial)) * (initial - 1)
    for i in range(initial + 1, number_of_nodes):
        perm = np.random.permutation(len(nodes))
        curr_deg = 0
        j = 0

        while (curr_deg < average_degree):
            ind = perm[j]
            ni = nodes[ind]
            if A[i, ni] == 0 and i != ni:
                A[i, ni] = 1
                A[ni, i] = 1
                nodes.append(i)
                nodes.append(ni)
                curr_deg += 1
            j += 1


def random_network(A):
    nr, nc = A.shape
    ch_r, ch_c = A.chunks
    #    ch_size = ch_r*ch_c
    for r in range(0, nr, ch_r):
        for c in range(0, nc, ch_c):
            r_f, r_t = r, r + ch_r
            c_f, c_t = c, c + ch_c
            #            print(r_f, r_t, c_f, c_t)
            A[r_f:r_t, c_f:c_t] = sparse.rand(ch_r, ch_c).toarray()


def create_network(file_name, size, ch_len, compression, shuffle, method=barabasi_albert):
    file = h5py.File(file_name, "w")
    dset = file.create_dataset("adjacency", (size, size),
                               chunks=(ch_len, ch_len),
                               fillvalue=0,
                               compression=compression,
                               shuffle=shuffle)

    st = time.time()
    method(dset)
    print('{:.2f}s'.format(time.time() - st))
    file.close()


def run(file_name, size=4096, chunk_size=512, compression='gzip', shuffle=False, method=random_network):
    create_network(file_name, size, chunk_size, compression, shuffle, method)


if __name__ == '__main__':
    size = 4096
    chunk_size = 512

    # file_name = "../data/network_{}_{}.hdf5".format(size, ch_len)
    file_name = "../data/random.hdf5"

    compression_filters = ["gzip", "lzf"]
    shuffle_filter = [True, False]

    compression = compression_filters[0]
    shuffle = shuffle_filter[1]

    run(file_name, size, chunk_size, compression, shuffle, barabasi_albert)