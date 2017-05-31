#!/usr/bin/env python

def get_help_data_12589():
    """
    Ingestion help.
    Data store of information to be presented when a help request is made for port 12589.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'ingest',
                        'endpoint': 'ingestrequest',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get a list of all ingestrequest records.',
                        'data_required': False,
                        'data_format': None,
                        'samples': [{
                                    'sample_request': 'ingestrequest',
                                    'sample_response': None
                        }]

                    },
                    {
                        'root': 'ingest',
                        'endpoint': 'ingestrequest/{id}',
                        'method': 'PUT',
                        'permission_required': True,
                        'description': 'Update an ingest request identified by the id provided.',
                        'data_required': True,
                        'data_format':  [
                                { 'name': 'username',
                                  'type': 'str',
                                  'description': 'The username responsible for the ingestrequest.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'state',
                                  'type': 'str',
                                  'description': 'An enumeration value.',
                                  'valid_values': ['STAGE'],
                                  'default': None
                                },
                                { 'name': 'reccurring',
                                  'type': 'bool',
                                  'description': '',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'options',
                                  'type': 'dict',
                                  'description': 'Ingestion options: \'csvName\'(str), \'maxNumFiles\'(int), ' +
                                                 '\'checkExistingFiles\'(bool), \'beginFileDate\'(str), ' +
                                                 '\'endFileDate\'(str)',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                        'samples': [{
                                    'sample_request': 'ingestrequest/76',
                                    'sample_data': {
                                                    "username": "ms804",
                                                    "state": "STAGE",
                                                    "options": {"csvName":"CE01ISSP_D00001_ingest",
                                                               "maxNumFiles":6,
                                                               "checkExistingFiles":"false",
                                                               "beginFileDate":"2013-04-06",
                                                               "endFileDate":"2017-04-06"},
                                                    "recurring": "true"
                                                    },
                                    'sample_response': None
                        }]
                    },
                    {
                        'root': 'ingest',
                        'endpoint': 'ingestrequest',
                        'method': 'POST',
                        'permission_required': True,
                        'description': 'Create an ingestrequest record.',
                        'data_required': True,
                        'data_format':
                            [
                                { 'name': 'username',
                                  'type': 'str',
                                  'description': 'The username responsible for the ingestrequest.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'state',
                                  'type': 'str',
                                  'description': 'An enumeration value.',
                                  'valid_values': ['STAGE'],
                                  'default': None
                                },
                                { 'name': 'reccurring',
                                  'type': 'bool',
                                  'description': '',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'options',
                                  'type': 'dict',
                                  'description': 'Ingestion options: \'csvName\'(str), \'maxNumFiles\'(int), ' +
                                                 '\'checkExistingFiles\'(bool), \'beginFileDate\'(str), ' +
                                                 '\'endFileDate\'(str)',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                        'samples': [{
                            'sample_request': 'ingestrequest',
                            'sample_data': {
                                            "username": "ms804",
                                            "state": "STAGE",
                                            "options": {"csvName":"CE01ISSP_D00001_ingest",
                                                       "maxNumFiles":6,
                                                       "checkExistingFiles":"false",
                                                       "beginFileDate":"2013-04-06",
                                                       "endFileDate":"2017-04-06"},
                                            "recurring": "true"
                                            },
                            'sample_response': None
                        }]

                    }
                ]
    return help_data
