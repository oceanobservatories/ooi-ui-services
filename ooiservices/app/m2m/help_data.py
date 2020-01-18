#!/usr/bin/env python

from ooiservices.app.m2m.help_data_12575 import get_help_data_12575
from ooiservices.app.m2m.help_data_12576 import get_help_data_12576
from ooiservices.app.m2m.help_data_12577 import get_help_data_12577
from ooiservices.app.m2m.help_data_12578 import get_help_data_12578
from ooiservices.app.m2m.help_data_12580 import get_help_data_12580
from ooiservices.app.m2m.help_data_12586 import get_help_data_12586
from ooiservices.app.m2m.help_data_12587_asset import get_help_data_12587_asset
from ooiservices.app.m2m.help_data_12587_events import get_help_data_12587_events
from ooiservices.app.m2m.help_data_12587_status import get_help_data_12587_status
#from ooiservices.app.m2m.help_data_12589 import get_help_data_12589
from ooiservices.app.m2m.help_data_12590 import get_help_data_12590
#from ooiservices.app.m2m.help_data_12591 import get_help_data_12591
from ooiservices.app.m2m.common import valid_port_keywords


def get_help_data(port, keyword=None):
    """
    Data stores of information to be presented when a help request is made. Indexed by port.
    For each port there is a list of dictionaries associated with various requests supported on that port.
    Supported ports(9): 12575, 12576, 12577, 12578, 12580, 12586, 12587, [12589], 12590, 12590
    """
    help_data = []

    # (12575) Preload
    if port == 12575:
        help_data = get_help_data_12575()

    # (12576) Sensor Inventory
    elif port == 12576:
        help_data = get_help_data_12576()

    # (12577) Alerts and Alarms
    elif port == 12577:
        help_data = get_help_data_12577()

    # (12578) QC
    elif port == 12578:
        help_data = get_help_data_12578()

    # (12580) Annotations
    elif port == 12580:
        help_data = get_help_data_12580()

    # (12586) Vocabulary
    elif port == 12586:
        help_data = get_help_data_12586()

    # (12587) Asset Management
    elif port == 12587:
        results = []
        help_data = get_help_data_12587_asset()
        help_data += get_help_data_12587_events()
        help_data += get_help_data_12587_status()
        if keyword in valid_port_keywords[port]:
            if keyword != 'all':
                keyword = normalize_keyword(keyword)
                for item in help_data:
                    if keyword in item['endpoint']:
                        results.append(item)
                help_data = results

    # (12589) Ingestion
    #elif port == 12589:
    #    help_data = get_help_data_12589()

    elif port == 12590:
        help_data = get_help_data_12590()

    # (12591) Ingestion
    #elif port == 12591:
    #    help_data = get_help_data_12591()

    return help_data


def normalize_keyword(keyword):

    if keyword == 'assets':
        keyword = 'asset'
    elif keyword == 'event':
        keyword = 'events'
    elif keyword == 'deployments':
        keyword = 'deployment'
    elif keyword == 'cruises':
        keyword = 'cruise'
    elif keyword == 'calibration':
        keyword = 'cal'

    return keyword