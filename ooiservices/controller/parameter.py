#!/usr/bin/env python
'''
ooiservices.controller.parameter

'''


from ooiservices.controller.base import ObjectController, ListController
from ooiservices import app
from flask import request
import requests


class ParameterListController(ListController):
    def get(self):
        if request.args.get('stream_id', None) is None:
            return self.response_HTTP404()

        stream_id = request.args.get('stream_id')
        return get_attribs_for_ref(stream_id)

def get_attribs_for_ref(stream_id):
    variable_list = []

    url = '%s/info/%s/index.json' % (ERDDAPURL, stream_id)
    ref_outline = requests.get(url)
    if not ref_outline.status_code == 200:
        app.logger.error("Failed to make connection to ERDDAP at %s" % url)
        return []

    d = ref_outline.json()['table']
    cols = d['columnNames']
    for i,c in enumerate(cols):
        if c == "Variable Name":
            break
    for r in d['rows']:
        if r[i] != "NC_GLOBAL" and r[i] not in variable_list and r[i] != "time":
            variable_list.append(r[i])

    if variable_list:
        app.logger.error(repr(variable_list))
    return variable_list
