# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""General plugin utils"""

import platform
import hashlib
import urllib
import json
import xbmc
import xbmcaddon


class Utils(object):
    """General plugin utils"""

    def __init__(self, kodi_base_url, constants):
        """
        Injects instances & the plugin handle

        :param kodi_base_url: Plugin base url
        :type kodi_base_url: string
        :param constants: Constants instance
        :type constants: resources.lib.Constants
        """
        self.constants = constants
        self.kodi_base_url = kodi_base_url

    def get_addon_data(self):
        """
        Returns the relevant addon data for the plugin,
        e.g. name, version, default fanart, base data path & cookie pathname

        :returns:  dict - Addon data
        """
        addon = self.get_addon()
        base_data_path = xbmc.translatePath(addon.getAddonInfo('profile'))
        return dict(
            plugin=addon.getAddonInfo('name'),
            version=addon.getAddonInfo('version'),
            fanart=addon.getAddonInfo('fanart'),
            base_data_path=base_data_path,
            cookie_path=base_data_path + 'COOKIE')

    def log(self, msg, level=xbmc.LOGNOTICE):
        """
        Logs a message to the Kodi log (default debug)

        :param msg: Message to be logged
        :type msg: mixed
        :param level: Log level
        :type level: int
        """
        addon_data = self.get_addon_data()
        xbmc.log('[' + addon_data.get('plugin') + '] ' + str(msg), level)

    def get_local_string(self, string_id):
        """
        Fetches a translated string from the po files

        :param string_id: Id of the string to be translated
        :type string_id: int
        :returns:  string - Translated string
        """
        src = xbmc if string_id < 30000 else self.get_addon()
        loc_string = src.getLocalizedString(string_id)
        if isinstance(loc_string, unicode):
            loc_string = loc_string.encode('utf-8')
        return loc_string

    def build_url(self, query):
        """
        Generates an URL for internal plugin navigation

        :param query: Map of request params
        :type query: dict
        :returns:  string - Url
        """
        return self.kodi_base_url + '?' + urllib.urlencode(query)

    def use_inputstream(self):
        """
        Determines if inoutstream can/should be used to play the videos

        Note: At least Kodi 17.4 & Inoutstream 2.0.7 are needed, because
        of HSL support

        :returns:  bool - Use inputstream to play videos
        """
        raw_setting = self.get_addon().getSetting('use_inputstream')
        if raw_setting == 'false':
            return False
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
        """
        Returns an Kodi addon instance

        :returns:  xbmcaddon.Addon - Addon instance
        """
        return xbmcaddon.Addon(self.constants.get_addon_id())

    @classmethod
    def generate_hash(cls, text):
        """
        Returns an hash for a given text

        :param text: String to be hashed
        :type text: string
        :returns:  string - Hash
        """
        return hashlib.sha224(text).hexdigest()

    @classmethod
    def capitalize(cls, sentence):
        """
        Capitalizes a sentence

        :param sentence: String to be capitalized
        :type sentence: string
        :returns:  string - Capitalized sentence
        """
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
        """
        Retrieves the Kodi version (Defaults to 17)

        :returns:  string - Kodi version
        """
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
        """
        Retrieves the Inputsteam version (Defaults to 1.0.0)

        :returns:  string - Inputsteam version
        """
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
        # ARM based Linux
        if platform.machine().startswith('arm'):
            return base.replace('%PL%', '(X11; CrOS armv7l 7647.78.0)')
        # x86 Linux
        return base.replace('%PL%', '(X11; Linux x86_64)')
