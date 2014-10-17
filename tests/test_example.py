#!/usr/bin/env python

import unittest

class TestExample(unittest.TestCase):
    def test_success(self):
        assert 1 == 1
    def test_failure(self):
        assert 1 == 0 
