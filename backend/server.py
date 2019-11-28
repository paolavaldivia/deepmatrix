#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 17:02:05 2016

@author: pao
"""

# python server.py


import json

from crossdomain import crossdomain
from flask import Flask
from flask import request

app = Flask(__name__)


def pairToJson(point):
    return {'x': point[0], 'y': point[1]}


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/matrixinfo', methods=['GET'])
@crossdomain(origin='*')
def get_matrix_info():
    mousePos = request.args.get('mpx'), request.args.get('mpy')
    imPos = request.args.get('ipx'), request.args.get('ipy')
    res = {'success': True, 'mousePos': pairToJson(mousePos), 'imageInfo': pairToJson(imPos)}
    return json.dumps(res), 200, {'ContentType': 'application/json'}


if __name__ == "__main__":
    app.run(debug=True)
