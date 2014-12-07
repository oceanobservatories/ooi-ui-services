#!/usr/bin/env python
'''
ooiservices.controller.stream

StreamObjectController
StreamListController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.stream import StreamModel
from ooiservices.config import ERDDAPURL
from ooiservices import app
from flask import request
from flask.ext.restful import Resource

import re
import time
import requests

CACHE_UPDATE = None
META_OUTLINE = None

class StreamController(ObjectController):

    def get(self, id):
        result = self.model.read(id)
        return result

class StreamListController(ListController):

    def get(self):
        stream_list = get_stream_list()
        if request.args.get('reference_designator', None):
            ref_def = request.args.get('reference_designator')
            ref_def = re.sub(r'-', '_', ref_def)
            stream_list = [ s for s in stream_list if ref_def in s['Dataset ID'] ]

        return stream_list

def get_stream_list():
    index = get_index()
    streams = []
    columns = index['table']['columnNames']
    for row in index['table']['rows']:
        stream = {}
        for i, ele in enumerate(row):
            stream[columns[i]] = ele
        stream['id'] = stream['Dataset ID']
        streams.append(stream)
    return streams

def get_index():
    global META_OUTLINE
    global CACHE_UPDATE
    if META_OUTLINE is None:
        cahce_update = time.time()
        url = ERDDAPURL+"/info/index.json"
        META_OUTLINE = requests.get(url)
        META_OUTLINE = META_OUTLINE.json()
    if CACHE_UPDATE < (time.time() + 60):
        cahce_update = time.time()
        url = ERDDAPURL+"/info/index.json"
        META_OUTLINE = requests.get(url)
        META_OUTLINE = META_OUTLINE.json()
    return META_OUTLINE

