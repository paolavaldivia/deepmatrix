# -*- coding: utf-8 -*-

"""
Created on Sat Apr 30 18:33:55 2016

Deep Zoom Images for Large Matrices
Based on https://github.com/openzoom/deepzoom.py

@author: paolalv
"""

import math
import os
import shutil
import xml.dom.minidom

import PIL.Image
import PIL.ImageOps
import h5py
# from scipy.misc import toimage


def _get_or_create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _get_files_path(path):
    return os.path.splitext(path)[0] + '_files'


def _remove(path):
    os.remove(path)
    tiles_path = _get_files_path(path)
    shutil.rmtree(tiles_path)


def pos2ind(pos):
    return pos[1] + pos[2] * 2


# %%


NS_DEEPZOOM = 'http://schemas.microsoft.com/deepzoom/2008'

DEFAULT_RESIZE_FILTER = PIL.Image.ANTIALIAS
DEFAULT_IMAGE_FORMAT = 'gif'

RESIZE_FILTERS = {
    'cubic': PIL.Image.CUBIC,
    'bilinear': PIL.Image.BILINEAR,
    'bicubic': PIL.Image.BICUBIC,
    'nearest': PIL.Image.NEAREST,
    'antialias': PIL.Image.ANTIALIAS,
    'lanczos': PIL.Image.LANCZOS
}

# TODO: tiff
IMAGE_FORMATS = {
    'jpg': 'jpg',
    'png': 'png',
    'gif': 'gif'
}


class DeepZoomImageDescriptor(object):
    def __init__(self, width=None, height=None,
                 tile_size=256, tile_overlap=1, tile_format='jpg'):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tile_overlap = tile_overlap
        self.tile_format = tile_format
        self._num_levels = None
        self._stop_level = None

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
        return self.num_levels - 1

    @property
    def stop_level(self):
        """Number of levels in the pyramid."""
        if self._stop_level is None:
            self._stop_level = int(math.ceil(math.log(self.tile_size, 2))) - 1
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
        w, h = self.get_dimensions(level)
        return (int(math.ceil(float(w) / self.tile_size)),
                int(math.ceil(float(h) / self.tile_size)))

    def get_tile_dimensions(self, level, column, row):
        """Bounding box of the tile (x1, y1, x2, y2)"""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        x = (column * self.tile_size)
        y = (row * self.tile_size)
        level_width, level_height = self.get_dimensions(level)
        w = self.tile_size
        h = self.tile_size
        w = min(w, level_width - x)
        h = min(h, level_height - y)
        return w, h

    def get_tile_bounds(self, level, column, row):
        """Bounding box of the tile (x1, y1, x2, y2)"""
        assert 0 <= level and level < self.num_levels, 'Invalid pyramid level'
        x = (column * self.tile_size)
        y = (row * self.tile_size)
        level_width, level_height = self.get_dimensions(level)
        w = self.tile_size + (1 if column == 0 else 2) * self.tile_overlap
        h = self.tile_size + (1 if row == 0 else 2) * self.tile_overlap
        w = min(w, level_width - x)
        h = min(h, level_height - y)
        return (x, y, x + w, y + h)


# %%

class ImageCreator(object):
    """Creates Deep Zoom images."""

    def __init__(self, tile_size=256, tile_format='gif',
                 image_mode='1', image_options=None,
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

    def _get_tile_path(self, level, row, col):
        level_dir = _get_or_create_path(os.path.join(self.image_files, str(level)))
        im_format = self.descriptor.tile_format
        tile_path = os.path.join(level_dir, '%s_%s.%s' % (col, row, im_format))
        return tile_path

    def _save_image(self, image, level, row, col):
        tile_path = self._get_tile_path(level, row, col)
        image.save(tile_path, **(self.image_options))

    def get_full_res_image(self, level, col, row):
        col_from, row_from, col_to, row_to = self.descriptor.get_tile_bounds(level, col, row)
        if col_from >= col_to or row_from >= row_to:
            return None
        data = self.dataset[row_from:row_to, col_from:col_to]
        if self.data_op:
            data = self.data_op(data)
        # image = toimage(data, high=1,
        #                 cmin=self.data_extent[0], cmax=self.data_extent[1],
        #                 mode=self.image_mode)

        image = PIL.Image.fromarray(data, mode=self.image_mode)
        return image

    def load_image(self, level, col, row):
        tile_path = self._get_tile_path(level, row, col)
        if os.path.exists(tile_path):
            image = PIL.Image.open(tile_path)
            return image
        return None

    def tiles(self):
        """Iterator for all tiles (post-order traversal). Returns (level, column, row) of a tile."""
        stack = []
        last = None

        max_level = self.descriptor.max_levels
        level = self.descriptor.stop_level
        node = (level, 0, 0)

        while len(stack) > 0 or node[0] <= max_level:
            if node and node[0] <= max_level:
                stack.append(node)
                l, c, r = node
                node = (l + 1, c * 2, r * 2)  # tl
            else:
                peek = stack[-1]
                l, c, r = peek
                peek_tr = l + 1, c * 2 + 1, r * 2
                if peek_tr[0] <= max_level and pos2ind(peek_tr) > pos2ind(last):
                    node = peek_tr
                else:
                    peek_bl = l + 1, c * 2, r * 2 + 1
                    if peek_bl[0] <= max_level and pos2ind(peek_bl) > pos2ind(last):
                        node = peek_bl
                    else:
                        peek_br = l + 1, c * 2 + 1, r * 2 + 1
                        if peek_br[0] <= max_level and pos2ind(peek_br) > pos2ind(last):
                            node = peek_br
                        else:
                            yield peek
                            last = stack.pop()
        while level >= 0:
            yield (level, 0, 0)
            level -= 1

    # TODO: from recursive to iterative
    def get_image_recursive(self, level, row, col):
        """Returns and saves the bitmap image at the given level."""
        assert 0 <= level and level < self.descriptor.num_levels, 'Invalid pyramid level'

        width, height = self.descriptor.get_tile_dimensions(level, col, row)  # self.descriptor.get_dimensions(level)
        if width <= 0 or height <= 0:
            return None

        if level < self.descriptor.stop_level:
            next_level = level + 1
            image = self.get_image_recursive(next_level, 0, 0)
            width, height = self.descriptor.get_dimensions(level)
            image = self._resize_image(image, width, height)

        elif level < self.descriptor.max_levels:
            next_level = level + 1
            # TODO: check dimensions for handling sizes other than powers of 2
            tl = self.get_image_recursive(next_level, row * 2, col * 2)
            tr = self.get_image_recursive(next_level, row * 2, col * 2 + 1)
            bl = self.get_image_recursive(next_level, row * 2 + 1, col * 2)
            br = self.get_image_recursive(next_level, row * 2 + 1, col * 2 + 1)
            n_width, n_height = width * 2, height * 2

            new_im = PIL.Image.new(self.image_mode, (n_width, n_height))
            if tl: new_im.paste(tl, (0, 0))
            if tr: new_im.paste(tr, (self.tile_size, 0))
            if bl: new_im.paste(bl, (0, self.tile_size))
            if br: new_im.paste(br, (self.tile_size, self.tile_size))

            image = self._resize_image(new_im, width, height)
        else:  # build tiles for chunks
            image = self.full_res_image(level, col, row)

        self._save_image(image, level, row, col)
        return image

    def get_coarsened_image(self, level, col, row):
        width, height = self.descriptor.get_tile_dimensions(level, col, row)  # self.descriptor.get_dimensions(level)
        if width <= 0 or height <= 0:
            return None

        next_level = level + 1
        tl = self.load_image(next_level, col * 2, row * 2)
        tr = self.load_image(next_level, col * 2 + 1, row * 2)
        bl = self.load_image(next_level, col * 2, row * 2 + 1)
        br = self.load_image(next_level, col * 2 + 1, row * 2 + 1)
        n_width, n_height = width * 2, height * 2

        new_im = PIL.Image.new(self.image_mode, (n_width, n_height))
        if tl: new_im.paste(tl, (0, 0))
        if tr: new_im.paste(tr, (self.tile_size, 0))
        if bl: new_im.paste(bl, (0, self.tile_size))
        if br: new_im.paste(br, (self.tile_size, self.tile_size))

        image = self._resize_image(new_im, width, height)

        return image

    def get_image(self, level, col, row):
        image = None
        if level == self.descriptor.max_levels:
            image = self.get_full_res_image(level, col, row)
        elif level >= self.descriptor.stop_level:
            image = self.get_coarsened_image(level, col, row)
        return image

    def create(self, source, dataset, destination, data_extent=None, data_op=None, image_pal=None):
        """Creates Deep Zoom image from source file and saves it to destination."""
        if data_extent is None:
            data_extent = [0, 1]
        file = h5py.File(source, "r")
        self.dataset = file[dataset]
        self.data_extent = data_extent
        self.data_op = data_op
        self.image_pal = image_pal

        height, width = self.dataset.shape
        print('ds', width, height)
        self.chunk_width, self.chunk_height = self.dataset.chunks

        self.descriptor = DeepZoomImageDescriptor(width=width,
                                                  height=height,
                                                  tile_size=self.tile_size,
                                                  tile_overlap=0,
                                                  tile_format=self.tile_format)
        self.image_files = _get_or_create_path(_get_files_path(destination))

        image = None
        for level, col, row in self.tiles():
            # print(level, col, row, image)
            if level >= self.descriptor.stop_level:
                image = self.get_image(level, col, row)
                if image: self._save_image(image, level, row, col)
            else:
                width, height = self.descriptor.get_dimensions(level)
                image = self._resize_image(image, width, height)
                self._save_image(image, level, 0, 0)

        file.close()
        # Create descriptor
        self.descriptor.save(destination)


# %%
if __name__ == '__main__':
    print('nothing here ¯\_(ツ)_/¯')
