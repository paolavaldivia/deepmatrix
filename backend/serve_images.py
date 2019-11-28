#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 17:02:05 2016

@author: pao
"""

# python serve_images.py


import io
import os
import PIL.Image

from crossdomain import crossdomain
from flask import Flask, Response
from flask import request, send_file

app = Flask(__name__)

DATA_DIR = '../data'
FILE_EXTENSION = '.gif'


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/data", methods=['GET'])
@crossdomain(origin='*')
def get_image_zxy():
    dataset_name = request.args.get('dataset')
    z, x, y = request.args.get('z'), request.args.get('x'), request.args.get('y')
    file_name = get_file_name(dataset_name, z, x, y)
    file_path = os.path.join(DATA_DIR, file_name)
    output = output_gif(read_image(file_path))
    return Response(output.getvalue(), mimetype='image/gif')


@app.route("/data_info", methods=['GET'])
@crossdomain(origin='*')
def get_data_info():
    dataset_name = request.args.get('dataset')
    file_path = os.path.join(DATA_DIR, dataset_name + '.dzi')
    return send_file(file_path, as_attachment=False)


def get_file_name(dataset_name, z, x, y):
    return os.path.join(dataset_name+'_files', z, str(x) + '_' + str(y) + FILE_EXTENSION)


def read_image(file_path):
    return PIL.Image.open(file_path)


def output_gif(img):
    output = io.BytesIO()
    img.save(output, 'GIF', transparency=0)
    return output


if __name__ == "__main__":
    app.run(debug=True, port=8050)
