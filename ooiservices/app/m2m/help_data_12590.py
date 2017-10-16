#!/usr/bin/env python


def get_help_data_12590():
    """
    Help for EDEX version information, including components..
    Data store of information to be presented when a help request is made for port 12590.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'versions',
                        'endpoint': 'versions',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get all EDEX version information for available components.',
                        'data_required': False,
                        'data_format': None,
                        'samples': [{
                                    'sample_request': 'versions',
                                    'sample_data': {},
                                    'sample_response': [
                                        {
                                          "component" : "uFrame",
                                          "version" : "1.2.6-sr1",
                                          "release" : "2017-09-25"
                                        }]
                        }]

                    },
                    {
                        'root': 'versions',
                        'endpoint': 'versions/<component>',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get all EDEX version information for a specific component.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'component',
                                  'type': 'string',
                                  'description': 'Valid EDEX component returned from /versions request.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'latest',
                                  'type': 'string',
                                  'description': 'Constant indicating request for most current version information.',
                                  'valid_values': 'latest',
                                  'default': None
                                }
                            ],
                        'samples': [{
                                    'sample_request': 'versions/uFrame',
                                    'sample_data': {'component': "uFrame"},
                                    'sample_response': [
                                                        "1.2.6-sr1",
                                                        "1.2.6",
                                                        "1.2.5",
                                                        "1.2.4",
                                                        "1.2.3",
                                                        "1.2.2",
                                                        "1.2.1",
                                                        "1.1.3"]
                                    },
                                    {
                                    'sample_request': 'versions/uFrame/latest',
                                    'sample_data': {'component': "uFrame"},
                                    'sample_response': {
                                                      "component" : "uFrame",
                                                      "version" : "1.2.6-sr1",
                                                      "notes" : [
                                                            "Enhance ingestion logging in EDEX. (12618)",
                                                            "Uncabled_ingest mode unable to start. (12581)",
                                                            "Fix DOI SQL Errors on uframe-test and production. (12580)",
                                                            "Add version endpoint. (12497)" ],
                                                      "release" : "2017-09-25"
                                                        }
                                    }]

                    }
                ]
    return help_data
