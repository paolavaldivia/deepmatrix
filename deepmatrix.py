# -*- coding: utf-8 -*-

"""
Created on Sat Apr 30 18:33:55 2016

Deep Zoom Images for Large Matrices
Based on https://github.com/openzoom/deepzoom.py

@author: paolalv
"""

import math
import os
import PIL.Image
import shutil
import h5py

from scipy.misc import toimage

from io import BytesIO


try:
    from urllib  import urlopen 
except ImportError:
    from urllib.request import urlopen
import xml.dom.minidom


def _get_or_create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def _clamp(val, min, max):
    if val < min:
        return min
    elif val > max:
        return max
    return val

def _get_files_path(path):
    return os.path.splitext(path)[0] + '_files'

def _remove(path):
    os.remove(path)
    tiles_path = _get_files_path(path)
    shutil.rmtree(tiles_path)
   
def safe_open(path):
    print(path)
    return BytesIO(urlopen(path).read())
    
#%%



NS_DEEPZOOM = 'http://schemas.microsoft.com/deepzoom/2008'

DEFAULT_RESIZE_FILTER = PIL.Image.ANTIALIAS
DEFAULT_IMAGE_FORMAT = 'png'

RESIZE_FILTERS = {
    'cubic': PIL.Image.CUBIC,
    'bilinear': PIL.Image.BILINEAR,
    'bicubic': PIL.Image.BICUBIC,
    'nearest': PIL.Image.NEAREST,
    'antialias': PIL.Image.ANTIALIAS,
    }

#TODO: tiff
IMAGE_FORMATS = {
    'jpg': 'jpg',
    'png': 'png',
    }


class DeepZoomImageDescriptor(object):
    def __init__(self, width=None, height=None,
                 tile_size=254, tile_overlap=1, tile_format='jpg'):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tile_overlap = tile_overlap
        self.tile_format = tile_format
        self._num_levels = None
        self._stop_level = None

    def open(self, source):
        """Intialize descriptor from an existing descriptor file."""
        doc = xml.dom.minidom.parse(safe_open(source))
        image = doc.getElementsByTagName('Image')[0]
        size = doc.getElementsByTagName('Size')[0]
        self.width = int(size.getAttribute('Width'))
        self.height = int(size.getAttribute('Height'))
        self.tile_size = int(image.getAttribute('TileSize'))
        self.tile_overlap = int(image.getAttribute('Overlap'))
        self.tile_format = image.getAttribute('Format')

    def save(self, destination):
        """Save descriptor file."""
        file = open(destination, 'wb')
        doc = xml.dom.minidom.Document()
        image = doc.createElementNS(NS_DEEPZOOM, 'Image')
        image.setAttribute('xmlns', NS_DEEPZOOM)
        image.setAttribute('TileSize', str(self.tile_size))
        image.setAttribute('Overlap', str(self.tile_overlap))
        image.setAttribute('Format', str(self.tile_format))
        size = doc.createElementNS(NS_DEEPZOOM, 'Size')
        size.setAttribute('Width', str(self.width))
        size.setAttribute('Height', str(self.height))
        image.appendChild(size)
        doc.appendChild(image)
        descriptor = doc.toxml(encoding='UTF-8')
        file.write(descriptor)
        file.close()

    @classmethod
    def remove(self, filename):
        """Remove descriptor file (DZI) and tiles folder."""
        _remove(filename)

    @property
    def num_levels(self):
        """Number of levels in the pyramid."""
        if self._num_levels is None:
            max_dimension = max(self.width, self.height)
            self._num_levels = int(math.ceil(math.log(max_dimension, 2))) + 1
        return self._num_levels
        
    @property
    def max_levels(self):
        """Number of levels in the pyramid."""
        return self.num_levels-1
    
    @property
    def stop_level(self):
        """Number of levels in the pyramid."""
        if self._stop_level is None:
            self._stop_level = int(math.ceil(math.log(self.tile_size, 2)))
        return self._stop_level

    def get_scale(self, level):
        """Scale of a pyramid level."""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        max_level = self.num_levels - 1
        return math.pow(0.5, max_level - level)

    def get_dimensions(self, level):
        """Dimensions of level (width, height)"""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        scale = self.get_scale(level)
        width = int(math.ceil(self.width * scale))
        height = int(math.ceil(self.height * scale))
        return (width, height)

    def get_num_tiles(self, level):
        """Number of tiles (columns, rows)"""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        w, h = self.get_dimensions( level )
        return (int(math.ceil(float(w) / self.tile_size)),
                int(math.ceil(float(h) / self.tile_size)))

    def get_tile_bounds(self, level, column, row):
        """Bounding box of the tile (x1, y1, x2, y2)"""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        offset_x = 0 if column == 0 else self.tile_overlap
        offset_y = 0 if row == 0 else self.tile_overlap
        x = (column * self.tile_size) - offset_x
        y = (row * self.tile_size) - offset_y
        level_width, level_height = self.get_dimensions(level)
        w = self.tile_size + (1 if column == 0 else 2) * self.tile_overlap
        h = self.tile_size + (1 if row == 0 else 2) * self.tile_overlap
        w = min(w, level_width  - x)
        h = min(h, level_height - y)
        return (x, y, x + w, y + h)
        
    def get_tile_dimensions(self, level, column, row):
        """Bounding box of the tile (x1, y1, x2, y2)"""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        offset_x = 0 if column == 0 else self.tile_overlap
        offset_y = 0 if row == 0 else self.tile_overlap
        x = (column * self.tile_size) - offset_x
        y = (row * self.tile_size) - offset_y
        level_width, level_height = self.get_dimensions(level)
        w = self.tile_size + (1 if column == 0 else 2) * self.tile_overlap
        h = self.tile_size + (1 if row == 0 else 2) * self.tile_overlap
        w = min(w, level_width  - x)
        h = min(h, level_height - y)
        return (x, y, x + w, y + h)
        
#%%

class ImageCreator(object):
    """Creates Deep Zoom images."""
    def __init__(self, tile_size=128, tile_format='png',
                 image_mode='L', image_options=None, 
                 resize_filter=None):
        self.tile_size = int(tile_size)
        self.tile_format = tile_format
        self.image_mode = image_mode
        self.image_options = image_options
        if not tile_format in IMAGE_FORMATS:
            self.tile_format = DEFAULT_IMAGE_FORMAT
        self.resize_filter = resize_filter
        
        
    def _resize_image(self, image, width, height):
        if (self.resize_filter is None) or (self.resize_filter not in RESIZE_FILTERS):
            image = image.resize((width, height), PIL.Image.ANTIALIAS)
        else:
            image = image.resize((width, height), RESIZE_FILTERS[self.resize_filter])
        return image

        
    #TODO: from recursive to iterative
    def get_image(self, level, row, col):
        """Returns the bitmap image at the given level."""
        assert 0 <= level and level < self.descriptor.num_levels, 'Invalid pyramid level'
        if level < self.descriptor.stop_level: #TODO: it's easy to make this part iterative
            next_level = level+1
            image = self.get_image(next_level, 0, 0)
            width, height = self.descriptor.get_dimensions(level)
            image = self._resize_image(image, width, height)
            
        elif level < self.descriptor.max_levels:
            next_level = level+1
            
            #TODO: check dimensions for handling sizes other than powers of 2
            tl = self.get_image(next_level, row*2, col*2)
            tr = self.get_image(next_level, row*2, col*2+1)
            bl = self.get_image(next_level, row*2+1, col*2)
            br = self.get_image(next_level, row*2+1, col*2+1)
            
            n_width, n_height = self.tile_size*2, self.tile_size*2 #self.descriptor.get_dimensions(next_level)
            new_im = PIL.Image.new(self.image_mode, (n_width, n_height)) 
            new_im.paste(tl, (0, 0))
            new_im.paste(tr, (self.tile_size, 0))
            new_im.paste(bl, (0, self.tile_size))
            new_im.paste(br, (self.tile_size, self.tile_size))
                    
            width, height = self.tile_size, self.tile_size #self.descriptor.get_dimensions(level)
            image = self._resize_image(new_im, width, height)
        else:
            col_from, row_from, col_to, row_to = self.descriptor.get_tile_bounds(level, col, row)
            data = self.dataset[row_from:row_to, col_from:col_to]
            image = toimage(data, 
                            cmin=self.data_extent[0], cmax=self.data_extent[1],
                            mode=self.image_mode)
        
        level_dir = _get_or_create_path(os.path.join(self.image_files, str(level)))
        im_format = self.descriptor.tile_format
        tile_path = os.path.join(level_dir,'%s_%s.%s'%(col, row, im_format))
        image.save(tile_path, **(self.image_options))
        
        return image
            
    
    def tiles(self, level):
        """Iterator for all tiles in the given level. Returns (column, row) of a tile."""
        columns, rows = self.descriptor.get_num_tiles(level)
        for column in range(columns):
            for row in range(rows):
                yield (column, row)

    def create(self, source, dataset, destination, data_extent=[0, 255]):
        """Creates Deep Zoom image from source file and saves it to destination."""
        file = h5py.File(source, "r")
        self.dataset = file[dataset]
        self.data_extent = data_extent

        width, height = self.dataset.shape
        self.chunk_width, self.chunk_height = self.dataset.chunks
        self.descriptor = DeepZoomImageDescriptor(width=width,
                                                  height=height,
                                                  tile_size=self.tile_size,
                                                  tile_overlap=0,
                                                  tile_format=self.tile_format)                                          
        print('opened ', source)
        print('  size: ', width, ' x ', height)
        print('  tile_size: ', self.tile_size)
        
        self.image_files = _get_or_create_path(_get_files_path(destination))
        
        level = 0
        self.get_image(level, 0, 0)

        file.close()
        # Create descriptor
        self.descriptor.save(destination)
     
#TODO: clean unnecesary code

#%%
if __name__ == '__main__':
    print('nothing here ¯\_(ツ)_/¯')

    
    
    