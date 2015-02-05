#!/usr/bin/env python
'''
redmine blueprint.

'''

__author__ = 'M@Campbell'

from flask import Blueprint

redmine = Blueprint('redmine', __name__)

from ooiservices.app.redmine import routes