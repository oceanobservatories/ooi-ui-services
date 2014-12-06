#!/usr/bin/env python

import pytest

def pytest_addoption(parser):
    parser.addoption('--postgres', action="store_true",
            help="Run postgres integration tests")

def pytest_runtest_setup(item): 
    if 'postgres' in item.keywords and not item.config.getoption('--postgres'):
        pytest.skip('need --postgres option to run')
