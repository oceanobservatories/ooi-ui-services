#!/usr/bin/env python

"""
Support for uframe vocabulary interface, utilized for display names.
"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app import cache
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.models import (Stream, StreamParameter)
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.config import get_uframe_vocab_info

import requests
import requests.exceptions
import requests.adapters
import json

CACHE_TIMEOUT = 172800


# Get vocabulary
@api.route('/vocab', methods=['GET'])
def get_vocabulary():
    """ Get dict of all vocabulary entries. Key is reference designator, value is display name.
    """
    try:
        vocab_dict = get_vocab()
        return jsonify({'vocab': vocab_dict})

    except Exception as err:
        message = 'Error getting uframe vocabulary; %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get vocab dictionary.
def get_vocab():
    """ Get 'vocab_dict' from cache or compiled, return vocab_dict.
    """
    debug = False
    vocab_dict = {}
    vocab_codes = {}
    try:
        # Get 'vocab_dict' if cached
        dict_cached = cache.get('vocab_dict')
        if dict_cached:
            vocab_dict = dict_cached

        # Get 'vocab_codes' if cached
        codes_cached = cache.get('vocab_codes')
        if codes_cached:
            vocab_codes = codes_cached

        # If either 'vocab_dict' or 'vocab_codes' is not cached, get and place in cache.
        if not vocab_dict or not vocab_codes:
            if debug: print '\n Cache vocabulary...'
            vocab_dict, codes = compile_vocab()
            cache.set('vocab_dict', vocab_dict, timeout=CACHE_TIMEOUT)
            cache.set('vocab_codes', codes, timeout=CACHE_TIMEOUT)
            if debug: print '\n Cached vocabulary...'

        return vocab_dict

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get long display name for reference designator.
def get_long_display_name_by_rd(rd):
    """ Get long display name for reference designator.
    """
    debug = False
    try:
        result = None
        vocab_dict = get_vocab()
        if vocab_dict:
            if rd in vocab_dict:
                result = vocab_dict[rd]['long_name']
            else:
                result = build_long_display_name(rd)
                if result is None:
                    if debug: print '\n rd: ', rd

        return result
    except Exception:
        raise


# Get display name for a reference designator.
def get_display_name_by_rd(rd):
    """ Get display name for a reference designator.
    """
    try:
        result = None
        vocab_dict = get_vocab()
        if vocab_dict:
            if rd in vocab_dict:
                result = vocab_dict[rd]['name']
            else:
                # Build display name
                result = build_display_name(rd)
                if result is None:
                    result = rd

        return result
    except Exception:
        raise


# Get RS array name.
def get_rs_array_display_name_by_rd(rd):
    """ Get display name for a reference designator.
    """
    name = None
    try:
        # Get 'vocab_codes' if cached
        codes_cached = cache.get('vocab_codes')
        if codes_cached:
            vocab_codes = codes_cached
            if 'rs_array_names' in vocab_codes:
                rs_array_codes = vocab_codes['rs_array_names']
                if rd in rs_array_codes:
                    name = rs_array_codes[rd]
        if name is None:
            name = 'Cabled'

        return name
    except Exception:
        raise


# Get vocabulary item for reference designator.
def get_vocab_dict_by_rd(rd):
    """ Get vocabulary items for reference designator.
    """
    try:
        result = None
        vocab_dict = get_vocab()
        if vocab_dict:
            if rd in vocab_dict:
                result = vocab_dict[rd]
            else:
                result = build_vocab_dict_item(rd)
        return result
    except Exception:
        raise


# Build vocabulary item for reference designator.
def build_vocab_dict_item(rd):
    """ Build vocab dict for rd when one is not available.
    """
    template = {
          'id': 0,
          'long_name': '',
          'name': '',
          'model': '',
          'manufacturer': '',
          'mindepth': 0,
          'maxdepth': 0
        }
    try:
        template['long_name'] = build_long_display_name(rd)
        template['name'] = build_long_display_name(rd)
        return template
    except Exception:
        return template


# Compile vocabulary.
def compile_vocab():
    """ Get list of vocab items from uframe (reference designator as key), None or exception.
    if successful, update cache 'vocab_dict'.

    Note: Used in tasks for scheduled cache updates.

    Sample input from uframe:
    [
        {
          "@class" : ".VocabRecord",
          "refdes" : "CE01ISSM",
          "vocabId" : 1951,
          "instrument" : "",
          "tocL1" : "Coastal Endurance",
          "tocL2" : "Oregon Inshore Surface Mooring",
          "tocL3" : ""
        },
        {
          "@class" : ".VocabRecord",
          "refdes" : "CE01ISSM-MFC31",
          "vocabId" : 1952,
          "instrument" : "",
          "tocL1" : "Coastal Endurance",
          "tocL2" : "Oregon Inshore Surface Mooring",
          "tocL3" : "Seafloor Multi-Function Node (MFN)"
        },
        . . .
    ]

    New Sample input from uframe:
    [
        {
          "@class" : ".VocabRecord",
          "model" : "Communications and Power Manager",
          "manufacturer" : "WHOI",
          "vocabId" : 3,
          "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
          "instrument" : "Platform Controller",
          "tocL1" : "Coastal Endurance",
          "tocL2" : "Oregon Inshore Surface Mooring",
          "tocL3" : "Seafloor Multi-Function Node (MFN)",
          "mindepth" : 25,
          "maxdepth" : 25
        },
        . . .
    ]

    Sample response dictionary:
    {
      "vocab": {
        "CE": {
          "id": 0,
          "long_name": "Coastal Endurance",
          "name": "Coastal Endurance"
        },
        "CE01ISSM": {
          "id": 0,
          "long_name": "Coastal Endurance Oregon Inshore Surface Mooring",
          "name": "Oregon Inshore Surface Mooring"
        },
        "CE01ISSM-MFC31": {
          "id": 0,
          "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)",
          "name": "Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)"
        },
        "CE01ISSM-MFC31-00-CPMENG000": {
          "id": 1953,
          "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN) - Platform Controller",
          "name": "Platform Controller"
        },
        . . .
    }

    New Sample response dictionary:
    {
      "vocab": {
        "CE": {
          "id": 0,
          "long_name": "Coastal Endurance",
          "name": "Coastal Endurance"
          "model" : "",
          "manufacturer" : "",
          "mindepth" : 0,
          "maxdepth" : 25
        },
        "CE01ISSM": {
          "id": 0,
          "long_name": "Coastal Endurance Oregon Inshore Surface Mooring",
          "name": "Oregon Inshore Surface Mooring"
          "model" : "",
          "manufacturer" : "",
          "mindepth" : 0,
          "maxdepth" : 25
        },
        "CE01ISSM-MFC31": {
          "id": 0,
          "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)",
          "name": "Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)"
          "model" : "",
          "manufacturer" : "",
          "mindepth" : 0,
          "maxdepth" : 25
        },
        "CE01ISSM-MFC31-00-CPMENG000": {
          "id": 1953,
          "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN) - Platform Controller",
          "name": "Platform Controller"
          "model" : "Communications and Power Manager",
          "manufacturer" : "WHOI",
          "mindepth" : 25,
          "maxdepth" : 25
        },
        . . .
    }

    New Sample response dictionary:
    {
        "CE01ISSM-MFD35": {
            "id": 0,
            "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)",
            "manufacturer": "",
            "maxdepth": 25,
            "mindepth": 25,
            "model": "",
            "name": "Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)"
        },
        "CE01ISSM-MFD35-00-DCLENG000": {
            "id": 5,
            "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN) - Data Concentrator Logger (DCL)",
            "manufacturer": "WHOI",
            "maxdepth": 25,
            "mindepth": 25,
            "model": "Data Concentrator Logger",
            "name": "Data Concentrator Logger (DCL)"
        },
        "CE01ISSM-MFD35-01-VEL3DD000": {
            "id": 6,
            "long_name": "Coastal Endurance Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN) - 3-D Single Point Velocity Meter",
            "manufacturer": "Nortek",
            "maxdepth": 25,
            "mindepth": 25,
            "model": "VECTOR",
            "name": "3-D Single Point Velocity Meter"
        },
        . . .
    }
    """
    array_names = {'RS': 'Cabled'}
    rs_array_names = {}
    results = {}        # vocabulary generated from uframe or COL vocab
    results_plus = {}   # additional vocabulary gleaned from original vocabulary source
    vocabulary = []
    codes = {}
    debug = False
    try:
        print '\n Compiling vocabulary...'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get vocabulary. Try uframe, if error, then get COL vocabulary. Must have vocabulary
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            # Get vocabulary from uframe.
            vocabulary = get_vocab_from_uframe()
            codes = create_vocabulary_codes(vocabulary)
        except Exception as err:
            message = 'uframe vocabulary error. %s' % str(err)
            current_app.logger.info(message)
            raise Exception(str(err))

        # Check vocabulary results were returned.
        updated_vocabulary = False
        if len(vocabulary) <= 0:
            message = 'uframe vocabulary error, length of vocabulary returned is 0.'
            current_app.logger.info(message)
            raise Exception(message)

        # Verify if vocabulary entries indicate an updated vocabulary.
        test = vocabulary[0]
        #print '\n verify vocabulary - check test element: ', test
        if len(test) > 7:
            updated_vocabulary = True
        if debug: print '\n verify vocabulary - Updated_vocabulary: ', updated_vocabulary
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Process each vocab item into list with one or more dictionaries. (make_vocabulary response)
        # Two step process:
        # 1. process all vocabulary provided by uframe into results
        # 2. re-process vocab to back fill arrays and other parts which can be gleaned from vocabulary.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for vocab in vocabulary:

            # Get reference designator
            rd = vocab['refdes']
            if rd not in results:

                len_rd = len(rd)
                if len_rd < 27:
                    if len_rd != 8 and len_rd != 14 and len_rd < 14:
                        continue

                if updated_vocabulary:
                    # Get field values: model, manufacturer, mindepth, maxdepth
                    model = ''
                    if 'model' in vocab:
                        model = vocab['model']
                    manufacturer = ''
                    if 'manufacturer' in vocab:
                        manufacturer = vocab['manufacturer']
                    mindepth = 0
                    if 'mindepth' in vocab:
                        mindepth = vocab['mindepth']

                    maxdepth = 0
                    if 'maxdepth' in vocab:
                        maxdepth = vocab['maxdepth']

                # Platform
                if len_rd == 14:
                    platform = rd
                    if platform not in results:
                        long_name = ' '.join([vocab['tocL1'], vocab['tocL2']])
                        long_name += ' - ' + vocab['tocL3']
                        name = vocab['tocL2'] + ' - ' + vocab['tocL3']      # changed
                        if long_name is not None and name is not None:
                            results[platform] = {'long_name': long_name, 'name': name, 'id': 0}

                # Mooring
                elif len_rd == 8:
                    subsite = rd
                    if subsite not in results:
                        long_name = ' '.join([vocab['tocL1'], vocab['tocL2']])
                        name = vocab['tocL2']
                        if long_name is not None and name is not None:
                            results[subsite] = {'long_name': long_name, 'name': name, 'id': 0}

                # Instrument (standard)
                elif len_rd == 27:
                    display_name, name, id = make_display_name(vocab)
                    if display_name is not None and name is not None:
                        results[rd] = {'long_name': display_name, 'name': name, 'id': id}

                # Instrument (irregular)
                elif len_rd > 14 and len_rd < 27:
                    display_name, name, id = make_display_name(vocab)
                    if display_name is not None and name is not None:
                        results[rd] = {'long_name': display_name, 'name': name, 'id': id}

                if updated_vocabulary:
                    results[rd]['model'] = model
                    results[rd]['manufacturer'] = manufacturer
                    results[rd]['mindepth'] = mindepth
                    results[rd]['maxdepth'] = maxdepth


        # Re-process for arrays and anything else which can be harvested for vocabulary display names.
        # Additions added to results_plus; if results_plus, then combine result_plus into results.
        # Add default for Cabled
        if 'RS' not in results_plus:
            long_name = 'Cabled'
            name = 'Cabled'
            results_plus['RS'] = {'long_name': long_name, 'name': name, 'id': 0}

        for vocab in vocabulary:

            # Get reference designator
            rd = vocab['refdes']
            len_rd = len(rd)
            if len_rd > 8:
                # Process array; note id set to 0
                array_code = rd[:2]
                if array_code:
                    # For RS array names use 4 character designation when adding codes data
                    if array_code =='RS':
                        if vocab['tocL1']:
                            key = rd[:8]
                            if key:
                                if key not in rs_array_names:
                                    rs_array_names[key] = vocab['tocL1']
                                    """
                                    if debug:
                                        print '\n debug -- added to rs_array_names(%d): %s' % \
                                              (len(rs_array_names), rs_array_names)
                                    """

                    else:
                        if array_code not in array_names:
                            array_names[array_code] = vocab['tocL1']
                        long_name = vocab['tocL1']
                        name = vocab['tocL1']
                        results_plus[array_code] = {'long_name': long_name, 'name': name, 'id': 0}

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If additional array entries desired in response.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if results_plus:
            if debug:
                print '\n debug -- len(results): ', len(results)
                print '\n debug -- len(results_plus): ', len(results_plus)
            results.update(results_plus)

        if rs_array_names:
            codes['rs_array_names'] = rs_array_names

        if debug:
            print '\n -- codes: %s' % json.dumps(codes, indent=4, sort_keys=True)
            print '\n -- final len(results): ', len(results)

            """
            keys = results.keys()
            keys.sort()
            print '\n debug -- final results.keys(): ', json.dumps(keys, indent=4, sort_keys=True)
            """

        # Return vocabulary results (list) and codes (dict)
        print '\n Completed compiling vocabulary...'
        return results, codes

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise


# Construct display name.
def make_display_name(data):
    """ Get instrument display name values from vocab element provided. Return long_name, name and id.
    Sample input data item:
        {
          "@class" : ".VocabRecord",
          "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
          "vocabId" : 1,
          "instrument" : "Buoy Controller Engineering",
          "tocL1" : "Endurance",
          "tocL2" : "OR Inshore Surface Mooring",
          "tocL3" : "Multi-Function Node"
        }
    """
    long_name = None
    name = None
    id = 0
    try:
        rd = data['refdes']
        rd_len = len(rd)

        # Process standard instruments
        if rd_len == 27:
            tmp = " ".join([data['tocL1'], data['tocL2']])
            long_name = " - ".join([tmp, data['tocL3'], data['instrument']])
            name = data['instrument']
            id = data['vocabId']
        # Irregular reference designators.
        elif rd_len > 14 and rd_len < 27:
            tmp = " ".join([data['tocL1'], data['tocL2']])
            long_name = " - ".join([tmp, data['tocL3'], data['instrument']])
            name = data['instrument']
            id = data['vocabId']
        else:
            message = 'Malformed reference designator (%s), cannot process vocabulary.' % rd
            current_app.logger.info(message)
        return long_name, name, id

    except Exception as err:
        message = 'Failed to assemble display_name for vocabulary; %s ' % str(err)
        current_app.logger.info(message)
        return None, None, 0


# Get vocabulary codes.
def create_vocabulary_codes(vocabs):
    """ Create codes dictionary from vocabulary provided; the codes dictionary stores semantics provided in vocabulary.
    """
    debug = False
    extra_nodes = {
        "AV": "AUV",
        "DP": "Wire-Following Profiler",
        "GL": "Coastal Glider",
        "LJ": "Low-Power JBox",
        "LV": "Low-Voltage Node",
        "MF": "Multi-Function Node",
        "MJ": "Medium-Power JBox",
        "PC": "200m Platform",
        "PD": "Profiler Docking Station",
        "PG": "Global Profiling Glider",
        "PN": "Primary Node",
        "SC": "Winch Controller",
        "SF": "Shallow Profiler",
        "XX": "Bench Instrument"
    }
    extra_arrays = {
        'RS': 'Cabled'
    }
    extra_subsites = {
        "ASPI": "ASPI"
    }

    # The codes dictionary stores semantics provided in vocabulary.
    codes = {'arrays': {}, 'subsites': {}, 'nodes': {}, 'classes': {}}
    arrays = extra_arrays
    subsites = extra_subsites
    nodes = extra_nodes
    classes = {}

    try:
        if debug: print '\n debug -- entered create_vocabulary_codes...'

        if not vocabs or vocabs is None:
            message = 'vocabulary provided is empty or None'
            raise Exception(message)

        # Process each vocabulary item
        for item in vocabs:

            rd = item['refdes']
            len_rd = len(rd)
            vocab = item.copy()

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # -- Compile codes for dynamic display name generation
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            subsite = None
            node = None
            instr = None
            if len_rd == 27 or (len_rd > 14 and len_rd < 27):
                subsite, node, instr = rd.split('-', 2)
            elif len_rd == 14:
                subsite, node = rd.split('-')
            elif len_rd == 8:
                subsite = rd
            else:
                print '\n debug malformed reference designator: ', rd
                continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process reference designator into components:
            #   array_code, subsite_code, node_code, instr_class, [temp vars: instr, port, instrument]
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            array_code = rd[:2]
            subsite_code = ''
            if subsite is not None:
                subsite_code = subsite[4:8]

            node_code = ''
            if node is not None:
                node_code = node[0:2]

            instr_class = ''
            if instr is not None:
                if '-' in instr:
                    port, instrument = instr.split('-')
                    if instrument:
                        if len(instrument) >= 5:
                            instr_class = instrument[0:5]
                        else:
                            instr_class = instrument

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Accumulate the information for codes array
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if array_code not in arrays:
                if vocab['tocL1']:
                    arrays[array_code] = vocab['tocL1']
            if subsite_code:
                if subsite_code not in subsites:
                    if vocab['tocL2']:
                        subsites[subsite_code] = vocab['tocL2']
            if node_code:
                if node_code not in nodes:
                    if vocab['tocL3']:
                        nodes[node_code] = vocab['tocL3']
            if instr_class:
                if instr_class not in classes:
                    if vocab['instrument']:
                        classes[instr_class] = vocab['instrument']

        # Compile information into codes dictionary.
        codes['arrays'] = arrays
        codes['subsites'] = subsites
        codes['nodes'] = nodes
        codes['classes'] = classes

        if debug: print '\n debug -- codes(%d): %s' % (len(codes), json.dumps(codes, indent=4, sort_keys=True) )
        return codes

    except Exception as err:
        message = 'Error processing vocabulary codes. %s' % str(err)
        current_app.logger.info(message)
        raise


# ========================================================================
# Vocabulary database queries for stream and stream parameters
# ========================================================================
def get_parameter_name_by_parameter(stream_parameter_name):
    """ Get parameter name using database.
    """
    debug = False
    streamParameter = StreamParameter.query.filter_by(stream_parameter_name = stream_parameter_name).first()
    if streamParameter is None or streamParameter is []:
        if debug: print '[param] ', stream_parameter_name
        return None
    stream_display_name = streamParameter.standard_name
    return stream_display_name


def get_stream_name_by_stream(stream):
    """ Get stream name using database.
    """
    debug = False
    _stream = Stream.query.filter_by(stream=stream).first()
    if _stream is None or _stream is []:
        if debug: print '[strem] ', stream
        return None
    stream_display_name = _stream.concatenated_name
    return stream_display_name


# ========================================================================
# utility functions
# ========================================================================
def get_vocab_from_uframe():
    """ Get vocab items from uframe. Return dict (with reference designator as key), None or exception.

    Sample response:
    [
        {
          "@class" : ".VocabRecord",
          "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
          "vocabId" : 1,
          "instrument" : "Buoy Controller Engineering",
          "tocL1" : "Endurance",
          "tocL2" : "OR Inshore Surface Mooring",
          "tocL3" : "Multi-Function Node"
        },
        ...
    ]

    New Sample response (August 2016):
    [
        {
          "@class" : ".VocabRecord",
          "model" : "Communications and Power Manager",
          "manufacturer" : "WHOI",
          "vocabId" : 3,
          "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
          "instrument" : "Platform Controller",
          "tocL1" : "Coastal Endurance",
          "tocL2" : "Oregon Inshore Surface Mooring",
          "tocL3" : "Seafloor Multi-Function Node (MFN)",
          "mindepth" : 25,
          "maxdepth" : 25
        },
    ]
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_vocab_info()
        url = uframe_url + '/vocab'
        extended_timeout = 5 * timeout_read
        response = requests.get(url, timeout=(timeout, extended_timeout))
        if response.status_code != 200:
            message = '(%d) Failed to successfully get vocabulary from uframe.' % response.status_code
            raise Exception(message)
        if not response or response is None:
            message = 'Failed to get uframe vocabulary; returned empty list.'
            raise Exception(message)
        try:
            result = response.json()
        except Exception as err:
            message = 'Malformed json response from uframe vocabulary. %s' % str(err)
            raise Exception(message)
        if not result or result is None:
            message = 'Empty (or None) result returned for uframe vocabulary.'
            raise Exception(message)
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe vocabulary.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe vocabulary.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error getting uframe vocabulary.  %s" % str(err)
        current_app.logger.info(message)
        raise


# Build long display name.
def build_long_display_name(rd):
    """ Get long display name for reference designator using the codes dictionary.
    """
    debug = False
    is_rs = False
    try:
        # Get 'vocab_dict' if cached, if not cached build cache, set and continue
        dict_cached = cache.get('vocab_codes')
        if dict_cached:
            vocab_codes = dict_cached
        else:
            vocab_dict, vocab_codes = compile_vocab()
            cache.set('vocab_dict', vocab_dict, timeout=CACHE_TIMEOUT)
            cache.set('vocab_codes', vocab_codes, timeout=CACHE_TIMEOUT)

        # Verify 'vocab_codes' has content, otherwise error
        if not vocab_codes:
            message = 'Vocabulary processing failed to obtain vocab_codes dictionary, unable to process.'
            current_app.logger.info(message)
            return None

        # Process reference designator using 'vocab_dict' and 'vocab_codes'
        len_rd = len(rd)
        if len_rd < 8:
            return None

        # Build display name for instrument
        rs_code = None
        array_code = rd[:2]
        if array_code == 'RS':
            is_rs = True
            rs_code = rd[:8]

        if len_rd == 27:

            if debug: print '\n (build long display name) reference designator \'%s\'.' % rd
            subsite, node, instr = rd.split('-', 2)
            subsite_code = subsite[4:8]
            node_code = node[0:2]
            port, instrument = instr.split('-')
            instr_class = instrument[0:5]

            line1 = None
            if is_rs:
                if rs_code in vocab_codes['rs_array_names']:
                    line1 = vocab_codes['rs_array_names'][rs_code]
            else:
                if array_code in vocab_codes['arrays']:
                    line1 = vocab_codes['arrays'][array_code]

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            line3 = None
            if node_code in vocab_codes['nodes']:
                line3 = vocab_codes['nodes'][node_code]

            line4 = None
            if instr_class in vocab_codes['classes']:
                line4 = vocab_codes['classes'][instr_class]

            if line1 is None or line2 is None or line3 is None or line4 is None:
                return None

            tmp = ' '.join([line1, line2])
            result = ' - '.join([tmp, line3, line4])

        # Build display name for platform (sample: RS01SBPD-DP01A)
        elif len_rd == 14:
            subsite, node = rd.split('-')
            subsite_code = subsite[4:8]
            node_code = node[0:2]

            line1 = None
            if is_rs:
                if rs_code in vocab_codes['rs_array_names']:
                    line1 = vocab_codes['rs_array_names'][rs_code]
            else:
                if array_code in vocab_codes['arrays']:
                    line1 = vocab_codes['arrays'][array_code]

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            line3 = None
            if node_code in vocab_codes['nodes']:
                line3 = vocab_codes['nodes'][node_code]

            if line1 is None or line2 is None or line3 is None:
                return None

            tmp = ' '.join([line1, line2])
            result = ' - '.join([tmp, line3])

        # Build display name for mooring (sample: RS01SBPD)
        elif len_rd == 8:
            subsite = rd
            subsite_code = subsite[4:8]

            line1 = None
            if is_rs:
                if rs_code in vocab_codes['rs_array_names']:
                    line1 = vocab_codes['rs_array_names'][rs_code]
            else:
                if array_code in vocab_codes['arrays']:
                    line1 = vocab_codes['arrays'][array_code]

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            if line1 is None or line2 is None:
                return None

            result = ' '.join([line1, line2])

        # Make long display name for irregular reference designator (sample: RS03AXPS-SF03A-04A-IP12)
        elif len_rd > 14 and len_rd < 27:
            if debug: print '\n (build long display name) Irregular reference designator \'%s\'.' % rd
            subsite, node, instr = rd.split('-', 2)  # subsite = 'CE01ISSM', node = 'MFC31'
            subsite_code = subsite[4:8]
            node_code = node[0:2]

            if not instr:
                message = 'Reference designator \'%s\' is malformed; unable to discern sensor.' % rd
                raise(message)

            port, instrument = instr.split('-')

            if not instrument:
                message = 'Reference designator \'%s\' is malformed; unable to discern instrument class.' % rd
                raise(message)

            instr_class = None
            if instrument:
                if len(instrument) > 5:
                    instr_class = instrument[0:5]
                else:
                    instr_class = instrument

            line1 = None
            if is_rs:
                if rs_code in vocab_codes['rs_array_names']:
                    line1 = vocab_codes['rs_array_names'][rs_code]
            else:
                if array_code in vocab_codes['arrays']:
                    line1 = vocab_codes['arrays'][array_code]

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            line3 = None
            if node_code in vocab_codes['nodes']:
                line3 = vocab_codes['nodes'][node_code]

            line4 = None
            if instr_class in vocab_codes['classes']:
                line4 = vocab_codes['classes'][instr_class]

            if line1 is None or line2 is None or line3 is None or line4 is None:
                return None

            tmp = ' '.join([line1, line2])
            result = ' - '.join([tmp, line3, line4])

        else:
            return None

        #print '\n\t ***** debug -- build_long_display_name - result: ', result
        return result

    except Exception as err:
        message = 'Exception in build display name for %s; %s' % (rd, str(err))
        current_app.logger.info(message)
        return None


# Build display name.
def build_display_name(rd):
    """ Get display name for reference designator using the codes dictionary.
    """
    debug = False
    is_rs = False
    try:
        # Get 'vocab_dict' if cached, if not cached build cache, set and continue
        dict_cached = cache.get('vocab_codes')
        if dict_cached:
            vocab_codes = dict_cached
        else:
            vocab_dict, vocab_codes = compile_vocab()
            cache.set('vocab_dict', vocab_dict, timeout=CACHE_TIMEOUT)
            cache.set('vocab_codes', vocab_codes, timeout=CACHE_TIMEOUT)

        # Verify 'vocab_codes' has content, otherwise error
        if not vocab_codes:
            message = 'Vocabulary processing failed to obtain vocab_codes dictionary, unable to process.'
            current_app.logger.info(message)
            return None

        # Process reference designator using 'vocab_dict' and 'vocab_codes'
        len_rd = len(rd)
        if len_rd < 8:
            return None

        # Build display name for instrument
        """
        rs_code = None
        array_code = rd[:2]
        if array_code == 'RS':
            is_rs = True
            rs_code = rd[:8]
        """

        if len_rd == 27:
            if debug: print '\n (build display name) reference designator \'%s\'.' % rd
            subsite, node, instr = rd.split('-', 2)
            port, instrument = instr.split('-')
            instr_class = instrument[0:5]
            line4 = None
            if instr_class in vocab_codes['classes']:
                line4 = vocab_codes['classes'][instr_class]
            if line4 is None:
                return None
            result = line4

        # Build display name for platform (subsite = 'CE01ISSM', node = 'MFC31')
        elif len_rd == 14:
            subsite, node = rd.split('-')
            node_code = node[0:2]
            subsite_code = subsite[4:8]

            line2 = None                                        # Added
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            line3 = None
            if node_code in vocab_codes['nodes']:
                line3 = vocab_codes['nodes'][node_code]

            #if line3 is None:
            if line2 is None or line3 is None:
                return None
            result = ' - '.join([line2, line3])

        # Build display name for mooring
        elif len_rd == 8:
            subsite = rd
            subsite_code = subsite[4:8]

            """
            line1 = None
            if is_rs:
                if rs_code in vocab_codes['rs_array_names']:
                    line1 = vocab_codes['rs_array_names'][rs_code]
            else:
                if array_code in vocab_codes['arrays']:
                    line1 = vocab_codes['arrays'][array_code]
            """

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            #if line1 is None or line2 is None:
            if line2 is None:
                return None

            #result = ' '.join([line1, line2])
            result = line2

        # Make display name for irregular reference designator
        elif len_rd > 14 and len_rd < 27:
            if debug: print '\n (build display name) Irregular reference designator \'%s\'.' % rd
            subsite, node, instr = rd.split('-', 2)

            if not instr:
                message = 'Reference designator \'%s\' is malformed; unable to discern sensor.' % rd
                raise(message)

            port, instrument = instr.split('-')
            if not instrument:
                message = 'Reference designator \'%s\' is malformed; unable to discern instrument class.' % rd
                raise(message)

            # Get instrument class
            instr_class = None
            if instrument:
                if len(instrument) > 5:
                    instr_class = instrument[0:5]
                else:
                    instr_class = instrument
            line4 = None
            if instr_class in vocab_codes['classes']:
                line4 = vocab_codes['classes'][instr_class]
            if line4 is None:
                return None
            result = line4
        else:
            return None

        #print '\n\t ***** debug -- build_display_name -- result: ', result
        return result
    except Exception as err:
        message = 'Exception in build display name for %s; %s' % (rd, str(err))
        current_app.logger.info(message)
        return None