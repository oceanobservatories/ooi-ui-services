#!/usr/bin/env python
'''
ooiservices.app.alfresco.__init__

Blueprint factory init for the alfresco application.
'''

__author__ = 'M@Campbell'

from flask import Blueprint

alfresco = Blueprint('alfresco', __name__)

from ooiservices.app.alfresco import routes

'''
routes will hold ONLY endpoints.  Please NO other methods.
'''
routes
