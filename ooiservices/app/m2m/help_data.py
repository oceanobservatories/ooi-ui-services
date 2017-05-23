#!/usr/bin/env python

from ooiservices.app.m2m.help_data_12575 import get_help_data_12575
from ooiservices.app.m2m.help_data_12576 import get_help_data_12576
from ooiservices.app.m2m.help_data_12577 import get_help_data_12577
from ooiservices.app.m2m.help_data_12580 import get_help_data_12580
from ooiservices.app.m2m.help_data_12586 import get_help_data_12586
from ooiservices.app.m2m.help_data_12587_asset import get_help_data_12587_asset
from ooiservices.app.m2m.help_data_12587_events import get_help_data_12587_events



def get_help_data(port):
    """
    Data stores of information to be presented when a help request is made. Indexed by port.
    For each port there is a list of dictionaries associated with various requests supported on that port.
    Supported ports(7): 12575, 12576, 12577, 12578, 12580, 12586, 12587
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

    # (12580) Annotations
    elif port == 12580:
        help_data = get_help_data_12580()

    # (12586) Vocabulary
    elif port == 12586:
        help_data = get_help_data_12586()

    # (12587) Asset Management
    elif port == 12587:
        help_data = get_help_data_12587_asset()
        help_data += get_help_data_12587_events()



    else:
        help = {
         12578: []
        }
        if port in help:
            help_data = help[port]

    print '\n debug ======= type(help_data): ', str(type(help_data))
    return help_data
