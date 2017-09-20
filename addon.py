# -*- coding: utf-8 -*-
# Module: default
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Kodi plugin for Telekom Sport (https://telekomsport.de)"""

from sys import argv
from urlparse import parse_qsl
from resources.lib.Cache import Cache
from resources.lib.Constants import Constants
from resources.lib.ContentLoader import ContentLoader
from resources.lib.Dialogs import Dialogs
from resources.lib.ItemHelper import ItemHelper
from resources.lib.Session import Session
from resources.lib.Settings import Settings
from resources.lib.Utils import Utils


# setup plugin base stuff
PLUGIN_HANDLE = int(argv[1])
KODI_BASE_URL = argv[0]

# init plugin object structure
CONSTANTS = Constants()
CACHE = Cache()
UTILS = Utils(kodi_base_url=KODI_BASE_URL)
DIALOGS = Dialogs(utils=UTILS)
ITEM_HELPER = ItemHelper(constants=CONSTANTS, utils=UTILS)
SETTINGS = Settings(utils=UTILS, dialogs=DIALOGS, constants=CONSTANTS)
SESSION = Session(constants=CONSTANTS, util=UTILS, settings=SETTINGS)
CONTENT_LOADER = ContentLoader(
    utils=UTILS,
    constants=CONSTANTS,
    session=SESSION,
    item_helper=ITEM_HELPER,
    cache=CACHE,
    plugin_handle=PLUGIN_HANDLE)


def router(paramstring, user, password):
    """
    Converts paramstrings into dicts & decide which
    method should be called in order to display contents

    :param user: Telekom account email address or user id
    :type user: str.
    :param password: Telekom account password
    :type password: str.
    :returns:  bool -- Matching route found
    """
    params = dict(parse_qsl(paramstring))
    keys = params.keys()
    processed = False
    # settings action routes
    if params.get('action') is not None:
        if params.get('action') == 'logout':
            SESSION.logout()
        else:
            SESSION.switch_account()
        processed = True
    # plugin list & video routes
    if SESSION.login(user, password) is True:
        # show main menue, selection of sport categories
        if len(keys) == 0 and processed is False:
            CONTENT_LOADER.show_sport_selection()
            processed = True
        # play a video
        if params.get('video_id') is not None and processed is False:
            CONTENT_LOADER.play(video_id=params.get('video_id'))
            processed = True
        # show details of the match found (gamereport, relive, interviews...)
        if params.get('target') is not None and processed is False:
            CONTENT_LOADER.show_match_details(
                params.get('target'),
                params.get('lane'),
                params.get('for'))
            processed = True
        # show list of found matches/videos
        if params.get('date') is not None and processed is False:
            CONTENT_LOADER.show_matches_list(
                params.get('date'),
                params.get('for'))
            processed = True
        # show contents scraped from the api (with website scraped id)
        if params.get('lane') is not None and processed is False:
            CONTENT_LOADER.show_event_lane(
                sport=params.get('for'),
                lane=params.get('lane'))
            processed = True
        # show contents (lanes) scraped from the website
        if params.get('for') is not None and processed is False:
            CONTENT_LOADER.show_sport_categories(
                sport=params.get('for'))
            processed = True
    else:
        # show login failed dialog if login didn't succeed
        DIALOGS.show_login_failed_notification()
        return processed


if __name__ == '__main__':
    # Load addon data & start plugin
    ADDON = UTILS.get_addon()
    ADDON_DATA = UTILS.get_addon_data()
    UTILS.log('Started (Version ' + ADDON_DATA.get('version') + ')')
    # show user settings dialog if settings are not complete
    # store the credentials if user added them
    if SETTINGS.has_credentials():
        USER, PASSWORD = SETTINGS.get_credentials()
    else:
        USER, PASSWORD = SETTINGS.set_credentials()
    # Call the router function and pass
    # the plugin call parameters to it.
    # We use string slicing to trim the
    # leading '?' from the plugin call paramstring
    router(argv[2][1:], user=USER, password=PASSWORD)
