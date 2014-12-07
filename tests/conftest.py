#!/usr/bin/env python

import pytest

def pytest_addoption(parser):
    parser.addoption('--postgres', action="store_true",
            help="Run postgres integration tests")
    parser.addoption('--sqlite', action="store_true",
            help="Run sqlite integration tests")
    parser.addoption('--erddap', action="store_true",
            help="Run erddap integration tests")

def pytest_runtest_setup(item): 
    if 'postgres' in item.keywords and not item.config.getoption('--postgres'):
        pytest.skip('need --postgres option to run')
    if 'sqlite_test' in item.keywords and not item.config.getoption('--sqlite'):
        pytest.skip('need --sqlite option to run')
    if 'erddap' in item.keywords and not item.config.getoption('--erddap'):
        pytest.skip('need --erddap option to run')
