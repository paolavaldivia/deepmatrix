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


def create_network(file_name, size, ch_size, compression, shuffle):
    file = h5py.File(file_name, "w")
    dset = file.create_dataset("adjacency", (size, size), 
                            chunks=(ch_size, ch_size),
                            fillvalue=0,
                            compression=compression,
                            shuffle=shuffle)
    
    st = time.time()
    barabasi_albert(dset, number_of_nodes=size)
    print('{:.2f}s'.format(time.time()-st))
    file.close()

if __name__ == '__main__':
    size = 8192
    ch_size = 128
    
    file_name = "network_{}_{}.hdf5".format(size, ch_size)
    
    compression_filters = ["gzip", "lzf"]
    shuffle_filter = [True, False]
    
    compression = compression_filters[0]
    shuffle = shuffle_filter[1]
    create_network(file_name, size, ch_size, compression, shuffle)
