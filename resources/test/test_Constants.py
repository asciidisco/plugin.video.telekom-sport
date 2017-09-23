# -*- coding: utf-8 -*-
# Module: Constants
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `Constants` module"""

import unittest
from resources.lib.Constants import Constants

class ConstantsTestCase(unittest.TestCase):
    """Tests for the `Constants` module"""

    def test_get_addon_id(self):
        """ADD ME"""
        constants = Constants()
        self.assertEqual(
            first=constants.get_addon_id(),
            second='plugin.video.telekom-sport')

    def test_get_base_url(self):
        """ADD ME"""
        constants = Constants()
        self.assertEqual(
            first=constants.get_base_url(),
            second='https://www.telekomsport.de')

    def test_get_login_link(self):
        """ADD ME"""
        constants = Constants()
        self.assertEqual(
            first=constants.get_login_link(),
            second='https://www.telekomsport.de/service/auth/web/login?headto=https://www.telekomsport.de/info')

    def test_get_login_endpoint(self):
        """ADD ME"""
        constants = Constants()
        self.assertEqual(
            first=constants.get_login_endpoint(),
            second='https://accounts.login.idm.telekom.com/sso')

    def test_get_epg_url(self):
        """ADD ME"""
        constants = Constants()
        self.assertEqual(
            first=constants.get_epg_url(),
            second='https://www.telekomsport.de/api/v1/')

    def test_get_stream_definition_url(self):
        """ADD ME"""
        base = 'https://www.telekomsport.de'
        route = '/service/player/streamAccess'
        params = '?videoId=%VIDEO_ID%&label=2780_hls'
        constants = Constants()
        self.assertEqual(
            first=constants.get_stream_definition_url(),
            second=base + route + params)

    def test_get_sports_list(self):
        """ADD ME"""
        constants = Constants()
        sports = constants.get_sports_list()
        sports_keys = sports.keys()
        self.assertIn('liga3', sports_keys)
        self.assertIn('del', sports_keys)
        self.assertIn('ffb', sports_keys)
        self.assertIn('fcb', sports_keys)
        self.assertIn('bbl', sports_keys)
        self.assertIn('bel', sports_keys)
        self.assertIn('skybuli', sports_keys)
        self.assertIn('skychamp', sports_keys)
        self.assertIn('skyhandball', sports_keys)

    def test_get_statics_list(self):
        """ADD ME"""
        constants = Constants()
        statics = constants.get_statics_list()
        statics_keys = statics.keys()
        self.assertIn('liga3', statics_keys)
