#!/usr/bin/env python
'''
Redmine blueprint.

'''
__author__ = 'M@Campbell'

from flask import Blueprint

redmine = Blueprint('redmine', __name__)

from ooiservices.app.redmine import controller