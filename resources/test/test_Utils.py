# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `Utils` module"""

import unittest
import mock
from resources.lib.Utils import Utils
from resources.lib.Constants import Constants
from resources.test.mocks.MockAddon import MockAddon

class UtilsTestCase(unittest.TestCase):
    """Tests for the `Utils` module"""

    def test_get_user_agent(self):
        """ADD ME"""
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.get_user_agent(),
            member='Chrome/59.0.3071.115')


    @mock.patch('platform.system')
    def test_get_user_agent_Linux(self, mock_system):
        """ADD ME"""
        mock_system.return_value = 'Linux'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.get_user_agent(),
            member='Linux')

    @mock.patch('platform.system')
    def test_get_user_agent_Darwin(self, mock_system):
        """ADD ME"""
        mock_system.return_value = 'Darwin'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.get_user_agent(),
            member='Mac')

    @mock.patch('platform.system')
    def test_get_user_agent_Windows(self, mock_system):
        """ADD ME"""
        mock_system.return_value = 'Windows'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.get_user_agent(),
            member='Win')

    @mock.patch('platform.system')
    @mock.patch('platform.machine')
    def test_get_user_agent_Windows(self, mock_machine, mock_system):
        """ADD ME"""
        mock_system.return_value = 'Linux'
        mock_machine.return_value = 'arm'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertIn(
            container=utils.get_user_agent(),
            member='armv')

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

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_inputstream_version_no_version(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"result": {"addon": {"enabled": true}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_inputstream_version(),
            second='1.0.0')

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_inputstream_version_disabled(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"result": {"addon": {"enabled": false}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_inputstream_version(),
            second='1.0.0')

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_inputstream_version_local_version(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"result": {"addon": {"enabled": true, "version": "2.1.7"}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_inputstream_version(),
            second='2.1.7')

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_inputstream_version_error_response(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"error": true}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_inputstream_version(),
            second='1.0.0')

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_kodi_version_no_version(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"result": {}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_kodi_version(),
            second=17)

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_kodi_version_local_version(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"result": {"version": {"major": 18}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_kodi_version(),
            second=18)

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_kodi_version_error_response(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"error": true}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_kodi_version(),
            second=17)

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_use_inputstream_error(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"error": true}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.use_inputstream(),
            second=False)

    @mock.patch('xbmc.executeJSONRPC')
    @mock.patch('xbmc.executeJSONRPC')
    def test_get_use_inputstream_success(self, mock_executeJSONRPC, mock_executeJSONRPC2):
        mock_executeJSONRPC.return_value = '{"result": {"version": {"major": 18}}}'
        mock_executeJSONRPC2.return_value = '{"result": {"addon": {"enabled": true, "version": "2.1.7"}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.use_inputstream(),
            second=True)

    @mock.patch('xbmc.executeJSONRPC')
    @mock.patch('xbmc.executeJSONRPC')
    def test_get_use_inputstream_high_inputstream(self, mock_executeJSONRPC, mock_executeJSONRPC2):
        mock_executeJSONRPC.return_value = '{"result": {"version": {"major": 18}}}'
        mock_executeJSONRPC2.return_value = '{"result": {"addon": {"enabled": true, "version": "12.1.7"}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.use_inputstream(),
            second=False)

    @mock.patch('xbmc.executeJSONRPC')
    def test_get_use_inputstream_low_inputstream(self, mock_executeJSONRPC):
        mock_executeJSONRPC.return_value = '{"result": {"version": {"major": 18}}}'
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        def return_low_version():
            return '0.9.9'
        utils.get_inputstream_version = return_low_version
        self.assertEquals(
            first=utils.use_inputstream(),
            second=False)

    @mock.patch('xbmcaddon.Addon')
    def test_get_use_inputstream_setting_off(self, mock_xbmcaddon):
        mock_xbmcaddon.return_value = MockAddon()
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.use_inputstream(),
            second=False)

    @mock.patch('xbmcaddon.Addon')
    def test_get_localized_string_unicode(self, mock_xbmcaddon):
        mock_xbmcaddon.return_value = MockAddon()
        utils = Utils(kodi_base_url='/foo/', constants=Constants())
        self.assertEquals(
            first=utils.get_local_string(30001),
            second='Foo')
