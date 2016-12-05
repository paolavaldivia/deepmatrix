
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 14:06:55 2016

@author: pao
"""

import deepmatrix

from string import Template

def _write_html(dzi_file, html_file='index.html'):
    with open('demo/template.html', 'r') as f_template:
        template = Template(f_template.read())
        with open(html_file, 'w') as f:
            f.write(template.substitute(dzi_file=dzi_file))

def invert(data):
    return 1-data
        
SOURCE = "data/random.hdf5"
DZI_FILE = "data/random.dzi"

DATASET = 'adjacency'
IMAGE_OPTIONS = {'compress_level': 0} #{'quality': 100}
HTML_FILE = "demo/index.html"

creator = deepmatrix.ImageCreator(tile_size=200, tile_format="png", 
                       image_mode='L', image_options=IMAGE_OPTIONS, 
                       resize_filter="lanczos")
creator.create(SOURCE, DATASET, DZI_FILE, 
               data_extent=[0, 1], 
               data_op=invert)

_write_html("../"+DZI_FILE, HTML_FILE)
