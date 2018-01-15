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
                        'endpoint': 'ingest/cal',
                        'method': 'POST',
                        'permission_required': True,
                        'description': 'Create a calibration ingest record.',
                        'data_required': True,
                        'data_format':
                            [
                                { 'name': 'username',
                                  'type': 'str',
                                  'description': 'The username responsible for the calibration ingestion request.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'data',
                                  'type': 'binary',
                                  'description': 'The binary contents of calibration ingestion spreadsheet.',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                        'samples': [{
                            'sample_request': 'ingest/cal',
                            'sample_data': {
                                            "username": "ooiusername",
                                            "data": 'binary_contents_of_xlsx_cal_ingest_spreadsheet_provided_here',

                                            },
                            'sample_response': {
                                    "message": [
                                        "EVENTA: Processing sheet [Asset_Cal_Info]:starting",
                                        "EVENTA: Attempt to add duplicate calibration data {[CC_scale_factor1:CALIBRATION_DATA:1411776000000:null]",
                                        "EVENTA: Attempt to add duplicate calibration data {[CC_scale_factor3:CALIBRATION_DATA:1411776000000:null]",
                                        "EVENTA: Attempt to add duplicate calibration data {[CC_scale_factor2:CALIBRATION_DATA:1411776000000:null]",
                                        "EVENTA: Attempt to add duplicate calibration data {[CC_scale_factor4:CALIBRATION_DATA:1411776000000:null]",
                                        "EVENTA: Calibration data added for sensor uid=ATAPL-58315-00002",
                                        "EVENTA: Processing sheet [Asset_Cal_Info]:complete"
                                    ],
                                    "status_code": 202
                                }
                        }]

                    }
                ]
    return help_data
