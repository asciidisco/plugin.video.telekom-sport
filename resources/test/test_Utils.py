# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `Utils` module"""

import unittest
from resources.lib.Utils import Utils
from resources.lib.Constants import Constants

class UtilsTestCase(unittest.TestCase):
    """Tests for the `Utils` module"""

    def test_get_user_agent(self):
        """ADD ME"""
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.get_user_agent(),
            member='Chrome/59.0.3071.115')

    def test_capitalize(self):
        """ADD ME"""
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.capitalize('foo bar'),
            second='Foo Bar')
        self.assertEquals(
            first=utils.capitalize('FOO BAR'),
            second='Foo Bar')
        self.assertEquals(
            first=utils.capitalize('Foo Bar'),
            second='Foo Bar')

    def test_generate_hash(self):
        """ADD ME"""
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.generate_hash('ABCDEFG'),
            second='bae3735e5822d8c30fafd70736316e7807f7cccf65e6e73c15f32a60')

    def test_get_addon(self):
        """ADD ME"""
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=str(utils.get_addon()),
            member='xbmcaddon.Addon')

    def test_build_url(self):
        """ADD ME"""
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.build_url({'bar': 'baz'}),
            member='/foo/?bar=baz')
