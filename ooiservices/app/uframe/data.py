#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

__author__ = 'Andy Bird'

import numpy as np
import calendar
import time
from dateutil.parser import parse
from datetime import datetime
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app import cache

