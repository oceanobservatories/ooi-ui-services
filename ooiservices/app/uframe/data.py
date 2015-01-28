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

def gen_data(start_date, end_date, sampling_rate, mean, std_dev):
    '''
    Returns a dictionary that contains the x coordinate time and the y
    coordinate which is random data normally distributed about the mean with
    the specified standard deviation.
    '''
    time0 = calendar.timegm(parse(start_date).timetuple())
    time1 = calendar.timegm(parse(end_date).timetuple())

    dt = sampling_rate # obs per second
    x = np.arange(time0, time1, dt)
    y = np.random.normal(mean, std_dev, x.shape[0])
    xy = np.array([x,y])

    row_order_xy = xy.T


    iso0 = datetime.utcfromtimestamp(time0).isoformat()
    iso1 = datetime.utcfromtimestamp(time1).isoformat()

    return {'size' : x.shape[0], 'start_time':iso0, 'end_time':iso1, 'cols':['x','y'], 'rows':row_order_xy.tolist()}

