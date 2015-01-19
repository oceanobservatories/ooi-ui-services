#!/usr/bin/env python
'''
Main app blueprint.

'''

__author__ = 'M.Campbell'

from flask import Blueprint

api = Blueprint('main', __name__)

from . import toc, authentication, user, operator_event