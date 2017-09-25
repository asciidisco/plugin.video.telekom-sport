# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""ADD ME"""

import platform
import hashlib
import urllib
import json
import xbmc
import xbmcaddon


class Utils(object):
    """ADD ME"""

    def __init__(self, kodi_base_url, constants):
        """ADD ME"""
        self.constants = constants
        self.kodi_base_url = kodi_base_url

    def get_addon_data(self):
        """ADD ME"""
        addon = self.get_addon()
        base_data_path = xbmc.translatePath(addon.getAddonInfo('profile'))
        return dict(
            plugin=addon.getAddonInfo('name'),
            version=addon.getAddonInfo('version'),
            fanart=addon.getAddonInfo('fanart'),
            base_data_path=base_data_path,
            cookie_path=base_data_path + 'COOKIE')

    def log(self, msg, level=xbmc.LOGNOTICE):
        """ADD ME"""
        addon_data = self.get_addon_data()
        xbmc.log('[' + addon_data.get('plugin') + '] ' + str(msg), level)

    def get_local_string(self, string_id):
        """ADD ME"""
        src = xbmc if string_id < 30000 else self.get_addon()
        loc_string = src.getLocalizedString(string_id)
        if isinstance(loc_string, unicode):
            loc_string = loc_string.encode('utf-8')
        return loc_string

    def build_url(self, query):
        """ADD ME"""
        return self.kodi_base_url + '?' + urllib.urlencode(query)

    def use_inputstream(self):
        """ADD ME"""
        kodi_version = int(self.get_kodi_version())
        inputstream_version_raw = self.get_inputstream_version()
        inputstream_version = int(inputstream_version_raw.replace('.', ''))
        if inputstream_version < 999:
            inputstream_version = inputstream_version * 10
        self.log('Kodi Version: ' + str(kodi_version))
        self.log('Inputstream Version: ' + str(inputstream_version))
        # determine if we can use inputstream for HLS
        use_inputstream = False
        if kodi_version >= 17 and inputstream_version >= 2070:
            use_inputstream = True
        return use_inputstream

    def get_addon(self):
        """ADD ME"""
        return xbmcaddon.Addon(self.constants.get_addon_id())

    @classmethod
    def generate_hash(cls, text):
        """ADD ME"""
        return hashlib.sha224(text).hexdigest()

    @classmethod
    def capitalize(cls, sentence):
        """ADD ME"""
        cap = ''
        words = sentence.decode('utf-8').split(' ')
        i = 0
        for word in words:
            if i > 0:
                cap += ' '
            cap += word[:1].upper() + word[1:].lower()
            i += 1
        return cap.encode('utf-8')

    @classmethod
    def get_kodi_version(cls):
        """ADD ME"""
        version = 17
        payload = {
            'jsonrpc': '2.0',
            'method': 'Application.GetProperties',
            'params': {
                'properties': ['version', 'name']
            },
            'id': 1
        }
        response = xbmc.executeJSONRPC(json.dumps(payload))
        responses_uni = unicode(response, 'utf-8', errors='ignore')
        response_serialized = json.loads(responses_uni)
        if 'error' not in response_serialized.keys():
            result = response_serialized.get('result', {})
            version_raw = result.get('version', {})
            version = version_raw.get('major', 17)
        return version

    @classmethod
    def get_inputstream_version(cls):
        """ADD ME"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'Addons.GetAddonDetails',
            'params': {
                'addonid': 'inputstream.adaptive',
                'properties': ['enabled', 'version']
            }
        }
        # execute the request
        response = xbmc.executeJSONRPC(json.dumps(payload))
        responses_uni = unicode(response, 'utf-8', errors='ignore')
        response_serialized = json.loads(responses_uni)
        if 'error' not in response_serialized.keys():
            result = response_serialized.get('result', {})
            addon = result.get('addon', {})
            if addon.get('enabled', False) is True:
                return addon.get('version', '1.0.0')
        return '1.0.0'

    @classmethod
    def get_user_agent(cls):
        """Determines the user agent string for the current platform

        :returns:  str -- User agent string
        """
        chrome_version = 'Chrome/59.0.3071.115'
        base = 'Mozilla/5.0 '
        base += '%PL% '
        base += 'AppleWebKit/537.36 (KHTML, like Gecko) '
        base += '%CH_VER% Safari/537.36'.replace('%CH_VER%', chrome_version)
        system = platform.system()
        # Mac OSX
        if system == 'Darwin':
            return base.replace('%PL%', '(Macintosh; Intel Mac OS X 10_10_1)')
        # Windows
        if system == 'Windows':
            return base.replace('%PL%', '(Windows NT 6.1; WOW64)')
        # x86 Linux
        return base.replace('%PL%', '(X11; Linux x86_64)')
