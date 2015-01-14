#!/usr/bin/env python
'''
Api blueprint.

'''

__author__ = 'M@Campbell'

from flask import Blueprint

api = Blueprint('api', __name__)

from . import toc, authentication, user