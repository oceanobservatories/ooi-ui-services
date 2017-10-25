#!/usr/bin/env python

def get_help_data_12591():
    """
    Calibration Ingestion help. (TBD)
    Data store of information to be presented when a help request is made for port 12591.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'ingest',
                        'endpoint': 'ingestrequest',
                        'method': 'POST',
                        'permission_required': True,
                        'description': 'Create a calibration ingest record.',
                        'data_required': True,
                        'data_format':
                            [
                                { 'name': 'username',
                                  'type': 'str',
                                  'description': 'The username responsible for the ingestrequest.',
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
