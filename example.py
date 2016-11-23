#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 14:06:55 2016

@author: pao
"""

import deepmatrix

from string import Template

def _write_html(dzi_file, html_file='index.html'):
    template = Template("""
    <div id="navigatorDiv" style="width: 200px; height: 200px; border: 2px"></div>
    <div id="openseadragon1" style="width: 200px; height: 200px;"></div>
    <script src="/openseadragon/openseadragon.js"></script>
    <script type="text/javascript">
        var viewer = OpenSeadragon({
            id: "openseadragon1",
            prefixUrl: "/openseadragon/images/",
            tileSources: "$dzi_file",
            maxZoomPixelRatio: 20,
            showNavigator:  true,
            navigatorId:   "navigatorDiv",
        });
    viewer.drawer.context.imageSmoothingEnabled = false;
    viewer.drawer.context.mozImageSmoothingEnabled = false;
    viewer.drawer.context.webkitImageSmoothingEnabled = false;
    </script>
    """)
    
    with open(html_file, 'w') as f:
        f.write(template.substitute(dzi_file=dzi_file))

def invert(data):
    return 1-data
        
SOURCE = "data/network_2048_128-128.hdf5"
DZI_FILE = "data/network.dzi"

DATASET = 'adjacency'
IMAGE_OPTIONS = {'compress_level': 0} #{'quality': 100}
HTML_FILE = "demo/index.html"

creator = deepmatrix.ImageCreator(tile_size=128, tile_format="png", 
                       image_mode='L', image_options=IMAGE_OPTIONS, 
                       resize_filter="bicubic")
creator.create(SOURCE, DATASET, DZI_FILE, data_extent=[0, 1], data_op=invert)

_write_html("../"+DZI_FILE, HTML_FILE)
