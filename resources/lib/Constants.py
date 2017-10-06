# -*- coding: utf-8 -*-
# Module: Constants
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""Static links & list of sports"""

# KODI addon id
ADDON_ID = 'plugin.video.telekom-sport'

# urls for login & data retrival
PRL = 'https://'
BASE_URL = PRL + 'www.telekomsport.de'
LOGIN_LINK = BASE_URL + '/service/auth/web/login?headto=' + BASE_URL + '/info'
LOGIN_ENDPOINT = PRL + 'accounts.login.idm.telekom.com/sso'
EPG_URL = BASE_URL + '/api/v1/'
STREAM_ROUTE = '/service/player/streamAccess'
STREAM_PARAMS = 'videoId=%VIDEO_ID%&label=2780_hls'
STREAM_DEFINITON_URL = BASE_URL + STREAM_ROUTE + '?' + STREAM_PARAMS
FANART_URL = PRL + 'raw.githubusercontent.com/hubsif/kodi-telekomsport/master'

# core event types
SPORTS = {
    'liga3': {
        'image': BASE_URL + '/images/packete/3liga.png',
        'fanart': FANART_URL + '/resources/fanart/3.liga.jpg',
        'name': '3. Liga',
        'indicators': ['3. Liga'],
        'page': 'fussball/3-liga',
        'epg': '',
    },
    'del': {
        'image': BASE_URL + '/images/packete/del.png',
        'fanart': FANART_URL + '/resources/fanart/del.jpg',
        'name': 'Deutsche Eishockey Liga',
        'indicators': [''],
        'page': 'eishockey/del',
        'epg': '',
    },
    'ffb': {
        'image': BASE_URL + '/images/packete/frauenbundesliga.png',
        'fanart': FANART_URL + '/resources/fanart/frauen-bundesliga.jpg',
        'name': 'Frauen-Bundesliga',
        'indicators': [''],
        'page': 'fussball/frauen-bundesliga',
        'epg': '',
    },
    'fcb': {
        'image': BASE_URL + '/images/packete/fcbayerntv.png',
        'fanart': FANART_URL + '/resources/fanart/fcbtv.jpg',
        'name': 'FC Bayern.TV',
        'indicators': [''],
        'page': 'fc-bayern-tv-live',
        'epg': '',
    },
    'bbl': {
        'image': BASE_URL + '/images/packete/easyCredit.png',
        'fanart': FANART_URL + '/resources/fanart/bbl.jpg',
        'name': 'Easycredit BBL',
        'indicators': [''],
        'page': 'basketball/bbl',
        'epg': '',
    },
    'bel': {
        'image': BASE_URL + '/images/packete/euroleague.png',
        'fanart': FANART_URL + '/resources/fanart/euroleague.jpg',
        'name': 'Basketball Turkish Airlines Euroleague',
        'indicators': [''],
        'page': 'basketball/euroleague',
        'epg': '',
    },
    'eurobasket': {
        'image': 'http://www.fiba.basketball/img/12104_logo_landscape.png',
        'fanart': FANART_URL + '/resources/fanart/eurobasket.jpg',
        'name': 'FIBA Eurobasket',
        'indicators': [''],
        'page': 'basketball/eurobasket2017',
        'epg': '',
    },
    'skybuli': {
        'image': BASE_URL + '/images/packete/sky-bundesliga.png',
        'fanart': FANART_URL + '/resources/fanart/bundesliga.jpg',
        'name': 'Sky Bundesliga',
        'indicators': [''],
        'page': 'sky/bundesliga',
        'epg': '',
    },
    'skychamp': {
        'image': BASE_URL + '/images/packete/sky-cl.png',
        'fanart': FANART_URL + '/resources/fanart/uefa.jpg',
        'name': 'Sky Champions League',
        'indicators': [''],
        'page': 'sky/champions-league',
        'epg': '',
    },
    'skyhandball': {
        'image': BASE_URL + '/images/packete/DKB.png',
        'fanart': FANART_URL + '/resources/fanart/hbl.jpg',
        'name': 'Handball Bundesliga',
        'indicators': [''],
        'page': 'sky/handball-bundesliga',
        'epg': '',
    },
}

# static menu items for various lists
STATICS = {
    'liga3': {
        'categories': [
            {
                'name': 'Alle Spieltage',
                'id': 'spieltage',
            }, {
                'name': 'Suche nach Datum',
                'id': 'bydate',
            }
        ]
    }
}


class Constants(object):
    """Access methods for static links & list of sports"""

    @classmethod
    def get_base_url(cls):
        """
        Returns the Telekom sport base HTTP address

        :returns:  string -- Base address
        """
        return BASE_URL

    @classmethod
    def get_login_link(cls):
        """
        Returns the Telekom Sport login HTTP route

        :returns:  string -- Login route
        """
        return LOGIN_LINK

    @classmethod
    def get_login_endpoint(cls):
        """
        Returns the Telekom login SSO endpoint

        :returns:  string -- SSO login endpoint
        """
        return LOGIN_ENDPOINT

    @classmethod
    def get_epg_url(cls):
        """
        Returns the EPG API URL

        :returns:  string -- EPG API URL
        """
        return EPG_URL

    @classmethod
    def get_stream_definition_url(cls):
        """
        Returns the stream defintion URL,
        used to get the final stream URL.
        It contains a `%VIDEO_ID%` placeholder,
        that needs to be replaced in order to
        fetch the streams

        :returns:  string -- EPG API URL
        """
        return STREAM_DEFINITON_URL

    @classmethod
    def get_sports_list(cls):
        """
        Returns the list of available sports

        :returns:  dict -- List of available sports
        """
        return SPORTS

    @classmethod
    def get_statics_list(cls):
        """
        Returns list of static menu items for various categories

        :returns:  dict -- List of static menu items for various categories
        """
        return STATICS

    @classmethod
    def get_addon_id(cls):
        """
        Returns the addon id

        :returns:  string -- Addon ID
        """
        return ADDON_ID
