#!/usr/bin/env python
'''
Main app blueprint.

'''

__author__ = 'M@Campbell'

from flask import Blueprint

api = Blueprint('main', __name__)

from ooiservices.app.main import routes, authentication, user, operator_event, annotation, instrument_deployment, \
    arrays, sys, c2, c2_mission, alertsalarms, notifications, notifications_redmine, user_event_notification
