# -*- coding: utf-8 -*-
# Module: default
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

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
try:
    PLUGIN_HANDLE = int(argv[1])
    KODI_BASE_URL = argv[0]
except ValueError:
    PLUGIN_HANDLE = 1
    KODI_BASE_URL = ''

# init plugin object structure
CONSTANTS = Constants()
CACHE = Cache()
UTILS = Utils(constants=CONSTANTS, kodi_base_url=KODI_BASE_URL)
DIALOGS = Dialogs(utils=UTILS)
ITEM_HELPER = ItemHelper(constants=CONSTANTS, utils=UTILS)
SETTINGS = Settings(utils=UTILS, dialogs=DIALOGS, constants=CONSTANTS)
SESSION = Session(constants=CONSTANTS, util=UTILS, settings=SETTINGS)
CONTENT_LOADER = ContentLoader(
    session=SESSION,
    item_helper=ITEM_HELPER,
    cache=CACHE,
    handle=PLUGIN_HANDLE)


def router(paramstring, user, password):
    """
    Converts paramstrings into dicts & decides which
    method should be called in order to display contents

    :param user: Telekom account email address or user id
    :type user: string
    :param password: Telekom account password
    :type password: string
    :returns:  bool -- Matching route found
    """
    params = dict(parse_qsl(paramstring))
    keys = params.keys()
    # settings action routes
    processed = __settings_action(params=params)
    # check login
    if __login_failed_action(user=user, password=password) is False:
        return False
    # plugin list & video routes
    # play a video
    processed = __play_action(params=params, processed=processed)
    # show details of the match found (gamereport, relive, interviews...)
    processed = __match_details_action(params=params, processed=processed)
    # show main menue, selection of sport categories
    processed = __sport_selection_action(keys=keys, processed=processed)
    # show contents (lanes) scraped from the website
    processed = __event_lane_action(params=params, processed=processed)
    # show list of found matches/videos
    processed = __categories_action(params=params, processed=processed)
    # show contents scraped from the api (with website scraped id)
    processed = __matches_list_action(params=params, processed=processed)
    return processed


def __settings_action(params):
    """
    Operates on actions from within the settings pane
    Can logout the user, can switch users account

    :param params: Route paramters
    :type params: dict
    :returns:  bool -- Route matched
    """
    if params.get('action') is not None:
        if params.get('action') == 'logout':
            SESSION.logout()
        else:
            SESSION.switch_account()
        return True
    return False


def __login_failed_action(user, password):
    """
    Veryfies the users login & shows a notification if it failes

    :param user: Telekom account email address or user id
    :type user: string
    :param password: Telekom account password
    :type password: string
    :returns:  bool -- Login succeeded
    """
    if SESSION.login(user, password) is False:
        # show login failed dialog if login didn't succeed
        DIALOGS.show_login_failed_notification()
        return False
    return True


def __sport_selection_action(keys, processed):
    """
    Show sport selection

    :param keys: Route paramters keys
    :type keys: list
    :param processed: Other route already matched
    :type processed: bool
    :returns:  bool -- Route matched
    """
    if len(keys) == 0 and processed is False:
        CONTENT_LOADER.show_sport_selection()
        return True
    return False


def __match_details_action(params, processed):
    """
    Show match details selection

    :param params: Route paramters
    :type params: dict
    :param processed: Other route already matched
    :type processed: bool
    :returns:  bool -- Route matched
    """
    if params.get('target') is not None and processed is False:
        CONTENT_LOADER.show_match_details(
            params.get('target'),
            params.get('lane'),
            params.get('for'))
        return True
    return False


def __matches_list_action(params, processed):
    """
    Show matches list selection

    :param params: Route paramters
    :type params: dict
    :param processed: Other route already matched
    :type processed: bool
    :returns:  bool -- Route matched
    """
    if params.get('date') is not None and processed is False:
        CONTENT_LOADER.show_matches_list(
            params.get('date'),
            params.get('for'))
        return True
    return False


def __event_lane_action(params, processed):
    """
    Show event lane selection

    :param params: Route paramters
    :type params: dict
    :param processed: Other route already matched
    :type processed: bool
    :returns:  bool -- Route matched
    """
    if params.get('lane') is not None and processed is False:
        CONTENT_LOADER.show_event_lane(
            sport=params.get('for'),
            lane=params.get('lane'))
        return True
    return False


def __categories_action(params, processed):
    """
    Show categories selection

    :param params: Route paramters
    :type params: dict
    :param processed: Other route already matched
    :type processed: bool
    :returns:  bool -- Route matched
    """
    _for = params.get('for')
    if _for is not None and processed is False:
        CONTENT_LOADER.show_sport_categories(
            sport=_for)
        return True
    return False


def __play_action(params, processed):
    """
   Play an item

    :param params: Route paramters
    :type params: dict
    :param processed: Other route already matched
    :type processed: bool
    :returns:  bool -- Route matched
    """
    video_id = params.get('video_id')
    if video_id is not None and processed is False:
        CONTENT_LOADER.play(video_id=video_id)
        return True
    return False


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
