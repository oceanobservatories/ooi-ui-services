#!/usr/bin/env python
'''
ooiservices

Initializes the application and necessary application logic
'''
from flask import Flask


app = Flask(__name__)

import ooiservices.routes # initialize the routes

