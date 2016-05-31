#!/usr/bin/env python

"""
Support for uframe vocabulary interface, utilized for display names.
"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app import cache
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.models import Platformname
from ooiservices.app.models import VocabNames
from ooiservices.app.models import Stream, StreamParameter
from ooiservices.app.main.errors import bad_request

import requests
import requests.exceptions
import requests.adapters

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800

# Remove when specific corrections areapplied to uframe data.
APPLY_VOCAB_CORRECTIONS = True

# Utilizes uframe vocab data to create additional vocab items from same uframe data.
VOCAB_PLUS = True


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


def get_vocab():
    """ Get 'vocab_dict' from cache or compiled, return vocab_dict.
    """
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
            vocab_dict, codes = _compile_vocab()
            cache.set('vocab_dict', vocab_dict, timeout=CACHE_TIMEOUT)
            cache.set('vocab_codes', codes, timeout=CACHE_TIMEOUT)

        return vocab_dict

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_long_display_name_by_rd(rd):
    """ Get long display name for reference designator.
    """
    try:
        result = None
        vocab_dict = get_vocab()
        if vocab_dict:
            if rd in vocab_dict:
                result = vocab_dict[rd]['long_name']
            else:
                result = _get_long_display_name_by_rd(rd)
                if result is None:
                    # build display name
                    result = build_long_display_name(rd)

        return result
    except Exception:
        raise


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
                # database to get display name
                result = _get_display_name_by_rd(rd)
                if result is None:
                    # build display name
                    result = build_display_name(rd)

        return result
    except Exception:
        raise


def _compile_vocab():
    """ Get list of vocab items from uframe. Return dict (with reference designator as key), None or exception.
    Update cache 'vocab_dict' is successful. This function called from tasks for scheduled cache updates.

    Sample input:
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

    Sample response dictionary (when VOCAB_PLUS enabled):
    {
        "CE01ISSM": {
          "id": 0,
          "long_name": "Endurance OR Inshore Surface Mooring",
          "name": "OR Inshore Surface Mooring"
        },
        "CE01ISSM-MFC31": {
          "id": 0,
          "long_name": "Endurance OR Inshore Surface Mooring Multi-Function Node",
          "name": "Multi-Function Node"
        },
        "CE01ISSM-MFC31-00-CPMENG000": {
          "id": 1,
          "long_name": "Endurance OR Inshore Surface Mooring Multi-Function Node Buoy Controller Engineering",
          "name": "Buoy Controller Engineering"
        },

        len(uframe vocab): (974):
        len(results): 974
        len(results_plus): 281
    """
    print '\n -- Compile vocabulary...'
    results = {}        # vocabulary generated from uframe vocab
    results_plus = {}   # additional vocabulary gleaned from uframe vocab
    try:

        # Get vocabulary from uframe.
        vocabs = get_vocab_from_uframe()

        """
        # If uframe vocabulary not available, return empty dicts.
        if not vocabs or vocabs is None:
            message = 'Vocabulary returned from uframe is empty; check uframe vocabulary configuration.'
            current_app.logger.info(message)
            raise Exception(message)
        """

        vocabulary, codes = preprocess_vocab_data(vocabs)

        # Process each vocab item into one or more dictionaries; return dict
        for vocab in vocabulary:

            # Process each vocab item
            rd = vocab['refdes']
            if rd not in results:

                len_rd = len(rd)

                # uframe currently provides only reference designators for instruments.
                if len_rd != 27:
                    message = 'Uframe vocab reference designator %s is not an instrument.' % rd
                    current_app.logger.info(message)
                    continue

                # Process uframe vocab consisting of instrument reference designators only.
                if len_rd == 27:

                    display_name, name, id = make_display_name(vocab)
                    if display_name is not None and name is not None:
                        results[rd] = {'long_name': display_name, 'name': name, 'id': id}

                    # Add additional information to resulting vocabulary (lighten dependency on db)
                    if VOCAB_PLUS:

                        # Process array; note id set to 0
                        array_code = rd[:2]
                        long_name = vocab['tocL1']
                        name = vocab['tocL1']
                        id = 0
                        results_plus[array_code] = {'long_name': long_name, 'name': name, 'id': 0}

                        # Process subsite (mooring); note id set to 0
                        subsite, node, _ = rd.split('-',2)
                        if subsite not in results:
                            long_name = ' '.join([ vocab['tocL1'], vocab['tocL2']])
                            name = vocab['tocL2']
                            if long_name is not None and name is not None:
                                results_plus[subsite] = {'long_name': long_name, 'name': name, 'id': 0}

                        # Process platform (subsite & node); note id set to 0
                        platform = '-'.join([subsite, node])
                        if platform not in results:
                            long_name = ' '.join([vocab['tocL1'], vocab['tocL2']])
                            long_name += ' - ' + vocab['tocL3']
                            name = vocab['tocL3']
                            if long_name is not None and name is not None:
                                results_plus[platform] = {'long_name': long_name, 'name': name, 'id': 0}

            else:
                message = 'Reference designator %s duplicate in uframe vocab response.' % rd
                current_app.logger.info(message)

        # If additional array and platform entries desired in response, use VOCAB_PLUS
        if VOCAB_PLUS:
            results.update(results_plus)

        return results, codes

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise


def make_display_name(data):
    """ Get display name values from data in vocab element provided. Return long_name, name and id.
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
        if rd_len == 27:
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
        return None, None, 0


def provide_vocab_correction(vocab):
    """ Some uframe vocabulary items need to be corrected/updated. (26)

    Basic data problems [4]
    RS01SBPS-PC01A-06-VADCPA101, id: 899
    RS01SLBS-LJ01A-05-HPIESA101, id: 913
    RS03AXBS-LJ03A-05-HPIESA301, id: 934
    RS03AXPS-PC03A-06-VADCPA301, id: 944

    ids 913 - 920 have 'tocL2' as 'Slope Base ' (extra space) [7]
    RS01SLBS-LJ01A-10-ADCPTE101, id: 914
    RS01SLBS-LJ01A-11-OPTAAC103, id: 915
    RS01SLBS-LJ01A-12-CTDPFB101, id: 916
    RS01SLBS-MJ01A-05-HYDLFA101, id: 917
    RS01SLBS-MJ01A-05-OBSBBA102, id: 918
    RS01SLBS-MJ01A-06-PRESTA101, id: 919
    RS01SLBS-MJ01A-12-VEL3DB101, id: 920

    bad_slope_base = ['RS01SLBS-LJ01A-10-ADCPTE101', 'RS01SLBS-LJ01A-11-OPTAAC103',
    'RS01SLBS-LJ01A-12-CTDPFB101', 'RS01SLBS-MJ01A-05-HYDLFA101', 'RS01SLBS-MJ01A-05-OBSBBA102',
    'RS01SLBS-MJ01A-06-PRESTA101', 'RS01SLBS-MJ01A-12-VEL3DB101']

    ids 943, 945 - 958 have 'tocL2' as 'Axial Base Shallow Profiler Mooring ' (extra space) [15]
    extra_space = ['RS03AXPS-PC03A-05-ADCPTD302', 'RS03AXPS-PC03A-07-CAMDSC302', 'RS03AXPS-PC03A-08-HYDBBA303',
    'RS03AXPS-PC03A-4A-CTDPFA303', 'RS03AXPS-PC03A-4B-PHSENA302', 'RS03AXPS-PC03A-4C-FLORDD303',
    'RS03AXPS-SF03A-2A-CTDPFA302', 'RS03AXPS-SF03A-2D-PHSENA301', 'RS03AXPS-SF03A-3A-FLORTD301',
    'RS03AXPS-SF03A-3B-OPTAAD301', 'RS03AXPS-SF03A-3C-PARADA301', 'RS03AXPS-SF03A-3D-SPKIRA301',
    'RS03AXPS-SF03A-4A-NUTNRA301', 'RS03AXPS-SF03A-4B-VELPTD302', 'RS03AXPS-SF03A-4F-PCO2WA301']

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    vocab item RS01SBPS-PC01A-06-VADCPA101:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS01SBPS-PC01A-06-VADCPA101",
          "vocabId" : 899,
          "instrument" : "5-Beam\"",
          "tocL1" : "",
          "tocL2" : "Cabled",
          "tocL3" : "Slope Base Shallow Profiler Mooring"
        },
    suggested correction:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS01SBPS-PC01A-06-VADCPA101",
          "vocabId" : 899,
          "instrument" : "5-Beam",
          "tocL1" : "Cabled",
          "tocL2" : "Slope Base Shallow Profiler Mooring",
          "tocL3" : "Platform Interface Controller"
        },

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    vocab item RS01SLBS-LJ01A-05-HPIESA101:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS01SLBS-LJ01A-05-HPIESA101",
          "vocabId" : 913,
          "instrument" : "Horizontal Electric Field\"",
          "tocL1" : "",
          "tocL2" : "Cabled",
          "tocL3" : "Slope Base "
        },
    suggested correction:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS01SLBS-LJ01A-05-HPIESA101",
          "vocabId" : 913,
          "instrument" : "Horizontal Electric Field",
          "tocL1" : "Cabled",
          "tocL2" : "Slope Base",
          "tocL3" : ""
        },
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    vocab item RS03AXBS-LJ03A-05-HPIESA301:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS03AXBS-LJ03A-05-HPIESA301",
          "vocabId" : 934,
          "instrument" : "Horizontal Electric Field\"",
          "tocL1" : "",
          "tocL2" : "Cabled",
          "tocL3" : "Axial Base"
        },
    suggested correction:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS03AXBS-LJ03A-05-HPIESA301",
          "vocabId" : 934,
          "instrument" : "Horizontal Electric Field",
          "tocL1" : "Cabled",
          "tocL2" : "Axial Base",
          "tocL3" : "Low-Power Jbox"
        },
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    vocab item RS03AXPS-PC03A-06-VADCPA301:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS03AXPS-PC03A-06-VADCPA301",
          "vocabId" : 944,
          "instrument" : "5-Beam\"",
          "tocL1" : "",
          "tocL2" : "Cabled",
          "tocL3" : "Axial Base Shallow Profiler Mooring "
        },
    suggested correction:
        {
          "@class" : ".VocabRecord",
          "refdes" : "RS03AXPS-PC03A-06-VADCPA301",
          "vocabId" : 944,
          "instrument" : "5-Beam",
          "tocL1" : "Cabled",
          "tocL2" : "Axial Base Shallow Profiler Mooring",
          "tocL3" : "Platform Interface Controller"
        },

    Sample of what applying the corrections does for you.........
    Without the corrections, the vocab data would be processed into:
    "RS01SBPS-PC01A-06-VADCPA101": {
      "id": 899,
      "long_name": " Cabled Slope Base Shallow Profiler Mooring 5-Beam\"",
      "name": "5-Beam\""
    },

    With corrections, the vocab data is processed into:
    "RS01SBPS-PC01A-06-VADCPA101": {
      "id": 899,
      "long_name": "Cabled Slope Base Shallow Profiler Mooring Platform Interface Controller 5-Beam",
      "name": "5-Beam"
    },
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    """
    bad_slope_base = ['RS01SLBS-LJ01A-10-ADCPTE101', 'RS01SLBS-LJ01A-11-OPTAAC103',
    'RS01SLBS-LJ01A-12-CTDPFB101', 'RS01SLBS-MJ01A-05-HYDLFA101', 'RS01SLBS-MJ01A-05-OBSBBA102',
    'RS01SLBS-MJ01A-06-PRESTA101', 'RS01SLBS-MJ01A-12-VEL3DB101']

    extra_space = ['RS03AXPS-PC03A-05-ADCPTD302', 'RS03AXPS-PC03A-07-CAMDSC302', 'RS03AXPS-PC03A-08-HYDBBA303',
    'RS03AXPS-PC03A-4A-CTDPFA303', 'RS03AXPS-PC03A-4B-PHSENA302', 'RS03AXPS-PC03A-4C-FLORDD303',
    'RS03AXPS-SF03A-2A-CTDPFA302', 'RS03AXPS-SF03A-2D-PHSENA301', 'RS03AXPS-SF03A-3A-FLORTD301',
    'RS03AXPS-SF03A-3B-OPTAAD301', 'RS03AXPS-SF03A-3C-PARADA301', 'RS03AXPS-SF03A-3D-SPKIRA301',
    'RS03AXPS-SF03A-4A-NUTNRA301', 'RS03AXPS-SF03A-4B-VELPTD302', 'RS03AXPS-SF03A-4F-PCO2WA301']

    gp_node_name_missing = ['GI02HYPM-GPM01-00-SIOENG000', 'GI02HYPM-GP001-00-ENG000000',
    'GP02HYPM-GPM01-00-SIOENG000', 'GA02HYPM-GP001-00-ENG000000']

    result = vocab.copy()
    rd = None
    try:
        rd = result['refdes']

        if rd == 'RS01SBPS-PC01A-06-VADCPA101':
            result = {
                      "@class": ".VocabRecord",
                      "refdes": "RS01SBPS-PC01A-06-VADCPA101",
                      "vocabId": 899,
                      "instrument": "5-Beam",
                      "tocL1": "Cabled",
                      "tocL2": "Slope Base Shallow Profiler Mooring",
                      "tocL3": "Platform Interface Controller"
                    }
        elif rd == 'RS03AXBS-LJ03A-05-HPIESA301':
            result = {
                      "@class": ".VocabRecord",
                      "refdes": "RS03AXBS-LJ03A-05-HPIESA301",
                      "vocabId": 934,
                      "instrument": "Horizontal Electric Field",
                      "tocL1": "Cabled",
                      "tocL2": "Axial Base",
                      "tocL3": "Low-Power Jbox"
                    }
        elif rd == 'RS03AXPS-PC03A-06-VADCPA301':
            result = {
                      "@class": ".VocabRecord",
                      "refdes": "RS03AXPS-PC03A-06-VADCPA301",
                      "vocabId": 944,
                      "instrument": "5-Beam",
                      "tocL1": "Cabled",
                      "tocL2": "Axial Base Shallow Profiler Mooring",
                      "tocL3": "Platform Interface Controller"
                    }
        elif rd == 'RS01SLBS-LJ01A-05-HPIESA101':
            result = {
                      "@class": ".VocabRecord",
                      "refdes": "RS01SLBS-LJ01A-05-HPIESA101",
                      "vocabId": 913,
                      "instrument": "Horizontal Electric Field",
                      "tocL1": "Cabled",
                      "tocL2": "Slope Base",
                      "tocL3": "Low-Power Jbox"
                    }

        elif rd in bad_slope_base or rd in extra_space:
            vocab['tocL2'] = vocab['tocL2'].strip()
            result = vocab

        elif rd in gp_node_name_missing:
            # No valid display name for 'GP' at this time, use 'GP'
            vocab['tocL3'] = "GP"
            result = vocab

        else:
            message = 'Unknown reference designator %s provided for correction.' % rd
            current_app.logger.info(message)
            result = vocab

        return result

    except Exception as err:
        message = 'Unknown issue while providing vocab update for reference designator %s. %s' % (rd, str(err))
        current_app.logger.info(message)
        return vocab


def preprocess_vocab_data(vocabs):
    """ Process uframe vocab items, build code dict. Apply uframe data updates. Return vocab and codes dict.

    http://ooiufs01.ooi.rutgers.edu:12576/sensor/inv
    subsites which are on production but missing from subsites dict:
    [
    "GA02HYPM", "SSRSPACC", "GP02HYPM", "GP05MOAS", "CE02SHBP", "CP04OSPM", "GS03FLMB",
    "RS03AXPS", "GI03FLMA", "GS03FLMA", "CE07SHSM", "CE04OSPD", "GI01SUMO", "CE07SHSP",
    "RS03AXBS", "RS03AXPD", "CE05MOAS", "GI05MOAS", "GA03FLMA", "RS03ASHS", "RS01SBPD",
    "GS05MOAS", "RS01SHBP", "RS03AXSM", "GS01SUMO", "CP05MOAS", "CE04OSBP", "GA03FLMB",
    "CE09OSPM", "CE02SHSP", "RS01SBPS", "CE02SHSM", "CE04OSSM", "RS03CCAL", "CP02PMCI",
    "RS03ECAL", "CE01ISSM", "CE01ISSP", "CP02PMCO", "GA05MOAS", "CE09OSSM", "RS03INT1",
    "RS03INT2", "GI02HYPM", "CE04OSPS", "RS01OSBP", "GP03FLMB", "RS01SHDR", "GP03FLMA",
    "CP03ISSM", "RS01SUM2", "CP03ISSP", "RS01SUM1", "CE06ISSP", "GI03FLMB", "CP02PMUI",
    "RS01SLBS", "CP01CNSM", "CE06ISSM", "GS02HYPM", "CP02PMUO", "CP01CNSP", "GA01SUMO",
    "CP04OSSM"
    ]

    Moorings with subsites not in codes (subsites: 'PACC', 'OSPD', 'AXPD', 'SBPD', 'AXSM', 'SHDR'):
    "SSRSPACC", "CE04OSPD", "RS03AXPD", "RS01SBPD", "RS03AXSM", "RS01SHDR"


    RS01SBPD-DP01A-03-FLCDRA102
    RS03AXPD-DP03A-04-FLNTUA302
    """

    extra_classes = {
        "CTDAV": "CTD AUV",
        "FLOBN": "Benthic Fluid Flow",
        "MASSP": "Mass Spectrometer",
        "OBSBK": "Broadband Ocean Bottom Seismometer",
        "OBSSK": "Short-Period Ocean Bottom Seismometer",
        "OSMOI": "Osmosis-Based Water Sampler",
        "PPSDN": "Particulate DNA Sampler",
        "RASFL": "Hydrothermal Vent Fluid Interactive Sampler",
        "ZPLSG": "Bio-acoustic Sonar (Global)",
        "HYDLF": "Low Frequency Acoustic Receiver (Hydrophone)",
        "FLCDR": "FLCDR",
        "FLNTU": "FLNTU"
    }

    extra_subsites = {
    "PACC": "PACC",
    "OSPD": "Offshore Profiler Dock",
    "AXPD": "Axial Base Profiler Dock",
    "SBPD": "Slope Base Profiler Dock",
    "AXSM": "Axial Base Surface Mooring",
    "SHDR": "Shelf Cabled DR",
    "ASPI": "ASPI"
    }

    extra_nodes = {
        "GP": "GP",
        "GL": "Coastal Glider",
        "PG": "Profiling Glider",
        "SC": "SC",
        "DP": "Deep Profiler",
        "PD": "PD",
        "XX": "Bench Instrument"
    }

    bad_slope_base = ['RS01SLBS-LJ01A-10-ADCPTE101', 'RS01SLBS-LJ01A-11-OPTAAC103',
    'RS01SLBS-LJ01A-12-CTDPFB101', 'RS01SLBS-MJ01A-05-HYDLFA101', 'RS01SLBS-MJ01A-05-OBSBBA102',
    'RS01SLBS-MJ01A-06-PRESTA101', 'RS01SLBS-MJ01A-12-VEL3DB101']

    extra_space = ['RS03AXPS-PC03A-05-ADCPTD302', 'RS03AXPS-PC03A-07-CAMDSC302', 'RS03AXPS-PC03A-08-HYDBBA303',
    'RS03AXPS-PC03A-4A-CTDPFA303', 'RS03AXPS-PC03A-4B-PHSENA302', 'RS03AXPS-PC03A-4C-FLORDD303',
    'RS03AXPS-SF03A-2A-CTDPFA302', 'RS03AXPS-SF03A-2D-PHSENA301', 'RS03AXPS-SF03A-3A-FLORTD301',
    'RS03AXPS-SF03A-3B-OPTAAD301', 'RS03AXPS-SF03A-3C-PARADA301', 'RS03AXPS-SF03A-3D-SPKIRA301',
    'RS03AXPS-SF03A-4A-NUTNRA301', 'RS03AXPS-SF03A-4B-VELPTD302', 'RS03AXPS-SF03A-4F-PCO2WA301']

    # vocab ids: 972, 973, 974 - Correct spelling error in axial seamount ('Disctrict' should be 'District')

    # vocab ids: 526, 621, 622, 706 node starts with 'GP', no tocL3
    gp_node_name_missing = ['GI02HYPM-GPM01-00-SIOENG000', 'GI02HYPM-GP001-00-ENG000000',
    'GP02HYPM-GPM01-00-SIOENG000', 'GA02HYPM-GP001-00-ENG000000']

    # Codes processing
    codes = {'arrays': {}, 'subsites': {}, 'nodes': {}, 'classes': {}}
    arrays = {}
    subsites = {}
    nodes = {}
    classes = {}
    results = []
    try:
        for item in vocabs:

            # Process each vocab item from uframe
            rd = item['refdes']
            len_rd = len(rd)
            if len_rd != 27:
                continue

            vocab = item.copy()

            # Correct bad records
            if APPLY_VOCAB_CORRECTIONS:

                # Correct spelling error in axial seamount ('Disctrict' should be 'District')
                a, b, c = rd.split('-', 2)
                if 'INT' in a:
                    if 'Disctrict' in vocab['tocL2']:
                        vocab['tocL2'] = vocab['tocL2'].replace('Disctrict','District')

                # Check for reference designators which have errant vocab data
                if rd == 'RS01SBPS-PC01A-06-VADCPA101' or \
                   rd == 'RS01SLBS-LJ01A-05-HPIESA101' or \
                   rd == 'RS03AXBS-LJ03A-05-HPIESA301' or \
                   rd == 'RS03AXPS-PC03A-06-VADCPA301' or \
                   rd in bad_slope_base or rd in extra_space or rd in gp_node_name_missing:

                    vocab = provide_vocab_correction(vocab)

            results.append(vocab)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # -- Compile codes for dynamic display name generation
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            subsite, node, instr = rd.split('-', 2)  # subsite = 'CE01ISSM', node = 'MFC31'
            array_code = rd[:2]
            subsite_code = subsite[4:8]
            node_code = node[0:2]
            port, instrument = instr.split('-')
            instr_class = instrument[0:5]

            if array_code not in arrays:
                arrays[array_code] = vocab['tocL1']

            if subsite_code not in subsites:

                subsite_text = vocab['tocL2']

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Remove context specific text in subsite (for endurance array).
                #   prefix = '' for 'CE05'
                #   prefix = 'OR ' for 'CE01', 'CE02', 'CE04'
                #   prefix = 'WA ' for 'CE06', 'CE07', 'CE09'
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                key = rd[0:4]
                if key == 'CE01' or key == 'CE02' or key == 'CE04' or \
                    key == 'CE06' or key == 'CE07' or key == 'CE09':
                    subsite_text = vocab['tocL2']
                    if subsite_text[0:3] == 'OR ' or subsite_text[0:3] == 'WA ':
                        subsite_text = subsite_text[3:]

                subsites[subsite_code] = subsite_text

            if node_code not in nodes:
                nodes[node_code] = vocab['tocL3']

            if instr_class not in classes:
                classes[instr_class] = vocab['instrument']

        # - - - - - - - - - - - - - - - - - - - - - - - - -
        # Extra classes - if not included in classes, add.
        # - - - - - - - - - - - - - - - - - - - - - - - - -
        for k, v in extra_classes.iteritems():
            if k not in classes:
                classes[k] = v

        # - - - - - - - - - - - - - - - - - - - - - - - - -
        # Extra subsites - if not included in subsites, add.
        # - - - - - - - - - - - - - - - - - - - - - - - - -
        for k, v in extra_subsites.iteritems():
            if k not in subsites:
                subsites[k] = v

        # - - - - - - - - - - - - - - - - - - - - - - - - -
        # Extra subsites - if not included in subsites, add.
        # - - - - - - - - - - - - - - - - - - - - - - - - -
        for k, v in extra_nodes.iteritems():
            if k not in nodes:
                nodes[k] = v

        # Compile information into codes dictionary.
        codes['arrays'] = arrays
        codes['subsites'] = subsites
        codes['nodes'] = nodes
        codes['classes'] = classes

        return results, codes

    except Exception as err:
        message = 'Error processing vocabulary data for \'vocab_codes\'. %s' % str(err)
        print '\n ', message
        current_app.logger.info(message)
        return vocabs, codes


def build_long_display_name(rd):
    """ Get long display name for reference designator using the codes dictionary.

    {
      "@class" : ".VocabRecord",
      "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
      "vocabId" : 1,
      "instrument" : "Buoy Controller Engineering",
      "tocL1" : "Endurance",
      "tocL2" : "OR Inshore Surface Mooring",
      "tocL3" : "Multi-Function Node"
    }

    Test cases:
        RS01SUM2-MJ01B-06-MASSPA101
        RS03INT1-MJ03C-06-MASSPA301
        GI03FLMA-RIS01-00-SIOENG000

    Sample:
    codes:  {
        "arrays": {
            "CE": "Endurance",
            "CP": "Pioneer",
            "GA": "Argentine Basin",
            "GI": "Irminger Sea",
            "GP": "Station Papa",
            "GS": "Southern Ocean",
            "RS": "Cabled"
        },
        "classes": {
            "ADCPA": "Velocity Profiler (short range) for mobile assets",
            "ADCPS": "Velocity Profiler (75 kHz)",
            "ADCPT": "Velocity Profiler (150kHz)",
            "BOTPT": "Bottom Pressure and Tilt",
            "CAMDS": "Digital Still Camera",
            "CAMHD": "HD Digital Video Camera",
            "CPMEN": "Buoy Controller Engineering",
            "CTDAV": "CTD AUV",
            "CTDBP": "CTD Pumped",
            "CTDGV": "CTD Glider",
            "CTDMO": "CTD Mooring (Inductive)",
            "CTDPF": "CTD Profiler",
            "D1000": "Temperature Sensor (on the RAS-PPS Seafloor Fluid Sampler)",
            "DCLEN": "Data Concentrator Logger (DCL) Engineering",
            "DOFST": "Dissolved Oxygen Fast Response",
            "DOSTA": "Dissolved Oxygen Stable Response",
            "ENG00": "Engineering",
            "FDCHP": "Direct Covariance Flux",
            "FLOBN": "Benthic Fluid Flow",
            "FLORD": "2-Wavelength Fluorometer",
            "FLORT": "3-Wavelength Fluorometer",
            "HPIES": "Horizontal Electric Field",
            "HYDBB": "Broadband Acoustic Receiver (Hydrophone)",
            "HYDGN": "Hydrogen Sensor",
            "HYDLF": "Low Frequency Acoustic Receiver (Hydrophone)",
            "MASSP": "Mass Spectrometer",
            "METBK": "Bulk Meteorology Instrument Package",
            "MOPAK": "3-Axis Motion Pack",
            "NUTNR": "Nitrate",
            "OBSBB": "Broadband Ocean Bottom Seismometer",
            "OBSBK": "Broadband Ocean Bottom Seismometer",
            "OBSSK": "Short-Period Ocean Bottom Seismometer",
            "OBSSP": "Short-Period Ocean Bottom Seismometer",
            "OPTAA": "Absorption Spectrophotometer",
            "OSMOI": "Osmosis-Based Water Sampler",
            "PARAD": "Photosynthetically Available Radiation",
            "PCO2A": "pCO2 Air-Sea",
            "PCO2W": "pCO2 Water",
            "PHSEN": "Seawater pH",
            "PPSDN": "Particulate DNA Sampler",
            "PRESF": "Seafloor Pressure",
            "PREST": "Tidal Seafloor Pressure",
            "RASFL": "Hydrothermal Vent Fluid Interactive Sampler",
            "RTE00": "Radar Target Enhancer (RTE)",
            "SIOEN": "Platform Controller Engineering",
            "SPKIR": "Spectral Irradiance",
            "SPPEN": "Surface Piercing Profiler Engineering",
            "STCEN": "Low Power Buoy Controller Engineering",
            "THSPH": "Hydrothermal Vent Fluid In-situ Chemistry",
            "TMPSF": "Diffuse Vent Fluid 3-D Temperature Array",
            "TRHPH": "Hydrothermal Vent Fluid Temperature and Resistivity",
            "VADCP": "5-Beam",
            "VEL3D": "3-D Single Point Velocity Meter",
            "VELPT": "Single Point Velocity Meter",
            "WAVSS": "Surface Wave Spectra",
            "WFPEN": "Wire-Following Profiler Engineering",
            "ZPLSC": "Bio-acoustic Sonar (Coastal)",
            "ZPLSG": "Bio-acoustic Sonar (Global)"
        },
        "nodes": {
            "FM": "Subsurface Buoy",
            "GL": "Coastal Glider",
            "GP": "GP",
            "LJ": "Low-Power Jbox",
            "LV": "Low-Voltage Node",
            "MF": "Multi-Function Node",
            "MJ": "Medium-Power Jbox",
            "PC": "Platform Interface Controller",
            "PG": "Profiling Glider",
            "PN": "Primary Node",
            "RI": "Mooring Riser",
            "SB": "Surface Buoy",
            "SC": "SC",
            "SF": "Shallow Profiler",
            "SP": "Surface Piercing Profiler",
            "WF": "Wire-Following Profiler"
        },
        "subsites": {
            "ASHS": "Axial Seamount ASHES",
            "AXBS": "Axial Base",
            "AXPD": "Axial Base Profiler Dock",
            "AXPS": "Axial Base Shallow Profiler Mooring",
            "AXSM": "Axial Base Surface Mooring",
            "CCAL": "Axial Seamount Central Caldera",
            "CNSM": "Central Surface Mooring",
            "CNSP": "Central Surface Piercing Profiler Mooring",
            "ECAL": "Axial Seamount Eastern Caldera",
            "FLMA": "Flanking Subsurface Mooring A",
            "FLMB": "Flanking Subsurface Mooring B",
            "HYPM": "Apex Profiler Mooring",
            "INT1": "Axial Seamount International District 1",
            "INT2": "Axial Seamount International District 2",
            "ISSM": "Inshore Surface Mooring",
            "ISSP": "Inshore Surface Piercing Profiler Mooring",
            "MOAS": "Mobile Asset",
            "OSBP": "Offshore Cabled Benthic Experiment Package",
            "OSPD": "Offshore Profiler Dock",
            "OSPM": "Offshore Profiler Mooring",
            "OSPS": "Offshore Cabled Shallow Profiler Mooring",
            "OSSM": "Offshore Surface Mooring",
            "PACC": "PACC",
            "PMCI": "Central Inshore Profiler Mooring",
            "PMCO": "Central Inshore Profiler Mooring",
            "PMUI": "Upstream Inshore Profiler Mooring",
            "PMUO": "Upstream Offshore Profiler Mooring",
            "SBPD": "Slope Base Profiler Dock",
            "SBPS": "Slope Base Shallow Profiler Mooring",
            "SHBP": "Shelf Cabled Benthic Experiment Package",
            "SHDR": "Shelf Cabled DR",
            "SHSM": "Shelf Surface Mooring ",
            "SHSP": "Shelf Surface Piercing Profiler Mooring",
            "SLBS": "Cabled",
            "SUM1": "Southern Hydrate Ridge Summit 1",
            "SUM2": "Southern Hydrate Ridge Summit 2",
            "SUMO": "Apex Surface Mooring"
        }
    }

    Notes:
    1. Nodes 'GP' is empty, set value to 'GP'.
    2. Subsites was missing the following, add (verification required):
    {
    "PACC": "PACC",
    "OSPD": "Offshore Profiler Dock",
    "AXPD": "Axial Base Profiler Dock",
    "SBPD": "Slope Base Profiler Dock",
    "AXSM": "Axial Base Surface Mooring",
    "SHDR": "Shelf Cabled DR"
    }

    3. Classes was missing the following, add (verification required):
    {
        "CTDAV": "CTD AUV",
        "FLOBN": "Benthic Fluid Flow",
        "MASSP": "Mass Spectrometer",
        "OBSBK": "Broadband Ocean Bottom Seismometer",
        "OBSSK": "Short-Period Ocean Bottom Seismometer",
        "OSMOI": "Osmosis-Based Water Sampler",
        "PPSDN": "Particulate DNA Sampler",
        "RASFL": "Hydrothermal Vent Fluid Interactive Sampler",
        "ZPLSG": "Bio-acoustic Sonar (Global)"
    }
    """
    try:
        # Get 'vocab_dict' if cached, if not cached build cache, set and continue
        dict_cached = cache.get('vocab_codes')
        if dict_cached:
            vocab_codes = dict_cached
        else:
            vocab_dict, vocab_codes = _compile_vocab()
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

        prefix = ''
        array_code = rd[:2]

        # For coastal endurance, check subsite and apply prefix as required.
        if array_code == 'CE':
            key = rd[0:3]
            if key == 'CE01' or key == 'CE02' or key == 'CE04':
                prefix = 'OR '
            elif key == 'CE06' or key == 'CE07' or key == 'CE09':
                prefix = 'WA '

        # Build display name for instrument
        if len_rd == 27:
            subsite, node, instr = rd.split('-', 2)  # subsite = 'CE01ISSM', node = 'MFC31'
            subsite_code = subsite[4:8]
            node_code = node[0:2]
            port, instrument = instr.split('-')
            instr_class = instrument[0:5]

            line1 = None
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

            if prefix:
                line2 = prefix + line2

            tmp = ' '.join([line1, line2])
            result = ' - '.join([tmp, line3, line4])

        # Build display name for platform sample: RS01SBPD-DP01A)
        elif len_rd == 14:
            subsite, node = rd.split('-')
            subsite_code = subsite[4:8]
            node_code = node[0:2]

            line1 = None
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

            if prefix:
                line2 = prefix + line2

            tmp = ' '.join([line1, line2])
            result = ' - '.join([tmp, line3])

        # Build display name for mooring
        elif len_rd == 8:
            subsite = rd
            subsite_code = subsite[4:8]

            line1 = None
            if array_code in vocab_codes['arrays']:
                line1 = vocab_codes['arrays'][array_code]

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            if line1 is None or line2 is None:
                return None

            if prefix:
                line2 = prefix + line2

            result = ' '.join([line1, line2])

        else:
            return None

        #print '\n\t ***** debug -- build_long_display_name - result: ', result
        return result

    except Exception as err:
        message = 'Exception in build display name for %s; %s' % (rd, str(err))
        current_app.logger.info(message)
        return None


def build_display_name(rd):
    """ Get display name for reference designator using the codes dictionary.

        "CE01ISSM": {
          "id": 0,
          "long_name": "Endurance OR Inshore Surface Mooring",
          "name": "OR Inshore Surface Mooring"
        },
        "CE01ISSM-MFC31": {
          "id": 0,
          "long_name": "Endurance OR Inshore Surface Mooring Multi-Function Node",
          "name": "Multi-Function Node"
        },
        "CE01ISSM-MFC31-00-CPMENG000": {
          "id": 1,
          "long_name": "Endurance OR Inshore Surface Mooring Multi-Function Node Buoy Controller Engineering",
          "name": "Buoy Controller Engineering"
        },

    {
      "@class" : ".VocabRecord",
      "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
      "vocabId" : 1,
      "instrument" : "Buoy Controller Engineering",
      "tocL1" : "Endurance",
      "tocL2" : "OR Inshore Surface Mooring",
      "tocL3" : "Multi-Function Node"
    }

    Test cases:
        RS01SUM2-MJ01B-06-MASSPA101
        RS03INT1-MJ03C-06-MASSPA301
        GI03FLMA-RIS01-00-SIOENG000

    """
    try:
        # Get 'vocab_dict' if cached, if not cached build cache, set and continue
        dict_cached = cache.get('vocab_codes')
        if dict_cached:
            vocab_codes = dict_cached
        else:
            vocab_dict, vocab_codes = _compile_vocab()
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

        # Prepare prefix processing for Endurance array vocab (tocL2)
        prefix = ''
        array_code = rd[:2]

        # For endurance array, check subsite and apply prefix as required.
        if array_code == 'CE':
            key = rd[0:3]
            if key == 'CE01' or key == 'CE02' or key == 'CE04':
                prefix = 'OR '
            elif key == 'CE06' or key == 'CE07' or key == 'CE09':
                prefix = 'WA '

        # Build display name for instrument
        if len_rd == 27:
            subsite, node, instr = rd.split('-', 2)  # subsite = 'CE01ISSM', node = 'MFC31'
            port, instrument = instr.split('-')
            instr_class = instrument[0:5]
            line4 = None
            if instr_class in vocab_codes['classes']:
                line4 = vocab_codes['classes'][instr_class]

            if line4 is None:
                return None

            result = line4

        # Build display name for platform
        elif len_rd == 14:
            subsite, node = rd.split('-')  # subsite = 'CE01ISSM', node = 'MFC31'
            node_code = node[0:2]
            line3 = None
            if node_code in vocab_codes['nodes']:
                line3 = vocab_codes['nodes'][node_code]

            if line3 is None:
                return None

            result = line3

        # Build display name for mooring
        elif len_rd == 8:
            subsite = rd
            subsite_code = subsite[4:8]

            line1 = None
            if array_code in vocab_codes['arrays']:
                line1 = vocab_codes['arrays'][array_code]

            line2 = None
            if subsite_code in vocab_codes['subsites']:
                line2 = vocab_codes['subsites'][subsite_code]

            if line1 is None or line2 is None:
                return None

            if prefix:
                line2 = prefix + line2

            result = ' '.join([line1, line2])

        else:
            return None

        #print '\n\t ***** debug -- build_display_name -- result: ', result
        return result
    except Exception as err:
        message = 'Exception in build display name for %s; %s' % (rd, str(err))
        current_app.logger.info(message)
        return None


# ========================================================================
# Vocabulary database queries; to be deprecated
# ========================================================================
"""
def _array_name(ref_des):
    array_des = ref_des[:2]
    try:
        array = VocabNames.query.with_entities(VocabNames.level_one).\
            filter_by(reference_designator=array_des).first()
        if array is not None:
            return array.level_one
    except Exception as e:
        print 'Unhandled exception in: ooiuiserivces.main.routes._array_name: %s.' % e
"""


def _platform_name(ref_des):
    platform_des = ref_des[:8]
    try:
        platform = VocabNames.query.with_entities(VocabNames.level_two).\
            filter_by(reference_designator=platform_des).first()
        if platform is not None:
            return platform.level_two
    except Exception:
        return None


def _assembly_name(ref_des):
    assembly_des = ref_des[:14]
    try:
        assembly = VocabNames.query.with_entities(VocabNames.level_three).\
            filter_by(reference_designator=assembly_des).first()
        if assembly is not None:
            return assembly.level_three
    except Exception:
        return None


def _instrument_name(ref_des):
    instrument_des = ref_des[:27]
    try:
        instrument = VocabNames.query.with_entities(VocabNames.level_four).\
            filter_by(reference_designator=instrument_des).first()
        if instrument is not None:
            return instrument.level_four
    except Exception:
        return None


def _get_display_name_by_rd(reference_designator):
    """ Get display name using vocab_dict for array; using database for platform, assembly, instrument.
    """
    #print '\n -- db lookup - _get_display_name_by_rd: ', reference_designator
    if len(reference_designator) == 2:
        #array = _array_name(reference_designator)
        array = get_display_name_by_rd(reference_designator)
        return array

    if len(reference_designator) == 8:
        platform = _platform_name(reference_designator)
        return platform

    if len(reference_designator) == 14:
        assembly = _assembly_name(reference_designator)
        return assembly

    if len(reference_designator) == 27:
        instrument = _instrument_name(reference_designator)
        return instrument


def _get_long_display_name_by_rd(reference_designator):
    """ Get long display name using database.
    """
    try:
        display_name = VocabNames.query.filter_by(reference_designator=reference_designator).first()
        if display_name is not None:
            tmp = ' '.join([display_name.level_one, display_name.level_two])
            display_name = ' - '.join([tmp, display_name.level_three, display_name.level_four])
        return display_name
    except Exception:
        return None


def get_platform_display_name_by_rd(reference_designator):
    """ Get platform display name using datanase.
    """
    #print '\n -- get_platform_display_name_by_rd: ', reference_designator
    platform = Platformname.query.filter_by(reference_designator=reference_designator[:14]).first()
    if platform is None:
        return None

    platform_display_name = platform.platform
    return platform_display_name


def get_parameter_name_by_parameter(stream_parameter_name):
    """ Get parameter name using database.
    """
    streamParameter = StreamParameter.query.filter_by(stream_parameter_name = stream_parameter_name).first()
    if streamParameter is None or streamParameter is []:
        return None

    stream_display_name = streamParameter.standard_name
    return stream_display_name


def get_stream_name_by_stream(stream):
    """ Get stream name using database.
    """
    stream = Stream.query.filter_by(stream=stream).first()
    if stream is None or stream is []:
        return None

    stream_display_name = stream.concatenated_name
    return stream_display_name

# ========================================================================
# utility functions
# ========================================================================

def get_uframe_vocab_info():
    """ Get uframe vocabulary configuration information.
    """
    try:
        uframe_url = current_app.config['UFRAME_VOCAB_URL']
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_VOCAB_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


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
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_vocab_info()
        url = uframe_url + '/vocab'
        response = requests.get(url, timeout=(timeout, timeout_read))
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