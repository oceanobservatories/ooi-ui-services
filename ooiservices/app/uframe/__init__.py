#!/usr/bin/env python
'''
uframe blueprint.

'''

__author__ = 'M@Campbell'

from flask import Blueprint

uframe = Blueprint('uframe', __name__)

from ooiservices.app.uframe import controller, assetController, data, assets, events, subscribe, vocab
