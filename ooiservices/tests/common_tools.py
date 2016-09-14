#!/usr/bin/env python
"""
Common supporting functions.

"""
__author__ = 'Edna Donoughe'


import json


def request_headers():
    """ Headers for uframe PUT and POST. """
    return {"Content-Type": "application/json"}

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Convert input to present all values as string, leaves nulls.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_event_input_as_string(data, debug=False):
    """ Take input from UI and present all values as string type. Leaves nulls.
    Handles one dict level down. Used to simulate UI data from jgrid submit.
    """
    try:
        if debug: print '\n debug -- get_event_input_as_string'
        #self.assertTrue(data is not None)
        #self.assertTrue(len(data) > 0)

        string_data = data.copy()
        keys = data.keys()
        for key in keys:
            if data[key] is not None:
                if not isinstance(data[key], dict):
                    string_data[key] = str(data[key])
                else:
                    if debug: print '\n Field is dict: ', key
                    tmp_dict = data[key].copy()
                    for k,v in tmp_dict.iteritems():
                        if v is not None:
                            if not isinstance(v, dict):
                                string_data[key][k] = str(v)
        return string_data

    except Exception as err:
        if debug: print '\n exception: ', str(err)
        raise


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Convert input to present all values as unicode, leaves nulls.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_event_input_as_unicode(data, debug=False):
    """ Take input from UI and present all values as string type. Leaves nulls.
    Handles one dict level down. Used to simulate UI data from jgrid submit.
    """
    try:
        string_data = data.copy()
        keys = data.keys()
        for key in keys:
            if data[key] is not None:
                if not isinstance(data[key], dict):
                    string_data[key] = unicode(data[key])
                else:
                    if debug: print '\n Field is dict: ', key
                    tmp_dict = data[key].copy()
                    for k,v in tmp_dict.iteritems():
                        if v is not None:
                            if not isinstance(v, dict):
                                string_data[key][k] = unicode(v)
        return string_data

    except Exception as err:
        if debug: print '\n exception: ', str(err)
        raise

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Dump dictionary provided if debug is enabled.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def dump_dict(dict, debug=False):
    """ Print dict if debug enabled.
    """
    if debug:
        print '\n --------------\n dictionary: %s' % json.dumps(dict, indent=4, sort_keys=True)


def get_asset_input_as_string(asset, debug=False):
    """ Take input from UI and present all values as string type. Leaves nulls.
    Handles one dict level down. Used to simulate UI data from jgrid submit.
    """
    try:
        if debug: print '\n debug -- get_asset_input_as_string'
        string_asset = asset.copy()
        keys = asset.keys()
        for key in keys:
            if asset[key] is not None:
                if not isinstance(asset[key], dict):
                    if not isinstance(asset[key], list):
                        string_asset[key] = str(asset[key])
                    else:
                        # Have a list to process...
                        list_value = asset[key]
                        if not list_value:
                            string_asset[key] = str(asset[key])
                        else:
                            if len(list_value) > 0:
                                if not isinstance(list_value[0], dict):
                                    string_asset[key] = str(asset[key])
                                else:
                                    #process list of dicts - stringize dict contents...
                                    #print '\n debug -- Have a list of dictionaries, field: ', key
                                    converted_list_value = []
                                    #print '\n debug -- len(converted_list_value): ', len(list_value)
                                    for remote in list_value:
                                        if debug: print '\n debug -- remote: ', remote
                                        tmp_dict = remote.copy()
                                        for k,v in tmp_dict.iteritems():
                                            #print '\n remote convert k: ', k
                                            if v is not None:
                                                if not isinstance(v, dict):
                                                    remote[k] = str(v)
                                        if debug: print '\n debug -- converted remote: ', remote
                                        converted_list_value.append(remote)
                                    string_asset[key] = str(converted_list_value)

                else:
                    if debug: print '\n Field is dict: ', key
                    tmp_dict = asset[key].copy()
                    for k,v in tmp_dict.iteritems():
                        if v is not None:
                            if not isinstance(v, dict):
                                string_asset[key][k] = str(v)
        if debug:
            print '\n debug ********get_asset_input_as_string ***********'
            print '\n string_asset(%d): ' % len(string_asset)
            dump_dict(string_asset, debug)
        return string_asset

    except Exception as err:
        if debug: print '\n exception: ', str(err)
        raise