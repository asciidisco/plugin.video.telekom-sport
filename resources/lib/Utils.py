"""ADD ME"""

import hashlib
import urllib
import json
import xbmc
import xbmcaddon


class Utils(object):
    """ADD ME"""

    def __init__(self, kodi_base_url):
        """ADD ME"""
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
            cookie_path=base_data_path + 'COOKIE'
        )

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
        inputstream_version = int(self.get_inputstream_version().replace('.', ''))
        if inputstream_version < 999:
            inputstream_version = inputstream_version * 10
        self.log('Kodi Version: ' + str(kodi_version))
        self.log('Inputstream Version: ' + str(inputstream_version))
        # determine if we can use inputstream for HLS
        use_inputstream = False
        if kodi_version >= 17 and inputstream_version >= 2070:
            use_inputstream = True
        return use_inputstream

    @classmethod
    def get_addon(cls):
        """ADD ME"""
        return xbmcaddon.Addon()

    @classmethod
    def generate_hash(cls, text):
        """ADD ME"""
        return hashlib.sha224(text).hexdigest()

    @classmethod
    def capitalize(cls, sentence):
        """ADD ME"""
        cap = ''
        words = sentence.decode('utf-8').split(' ')
        for word in words:
            cap += word[:1].upper() + word[1:].lower()
            cap += ' '
        return cap.encode('utf-8')

    @classmethod
    def get_kodi_version(cls):
        """ADD ME"""
        json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query = json.loads(json_query)
        version_installed = 17
        if json_query.get('result', {}).has_key('version'):
            version_installed = json_query['result']['version'].get('major', 17)
        return version_installed

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
        data = json.loads(response)
        if 'error' not in data.keys():
            result = data.get('result', {})
            addon = result.get('addon', {})
            if addon.get('enabled', False) is True:
                return addon.get('version', '1.0.0')
        return '1.0.0'
