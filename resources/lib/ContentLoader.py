# -*- coding: utf-8 -*-
# Module: ContentLoader
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""Fetches and parses content from the Telekom Sport API & website"""

import re
import json
import xml.etree.ElementTree as ET
from datetime import date
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup


class ContentLoader(object):
    """Fetches and parses content from the Telekom Sport API & website"""

    def __init__(self, cache, session, item_helper, handle):
        """
        Injects instances & the plugin handle

        :param cache: Cache instance
        :type cache: resources.lib.Cache
        :param session: Session instance
        :type session: resources.lib.Session
        :param item_helper: ItemHelper instance
        :type item_helper: resources.lib.ItemHelper
        :param handle: Kodis plugin handle
        :type handle: int
        """
        self.constants = session.constants
        self.utils = session.utils
        self.cache = cache
        self.session = session
        self.item_helper = item_helper
        self.plugin_handle = handle
        addon = self.utils.get_addon()
        verify_ssl = True if addon.getSetting('verifyssl') == 'True' else False
        self.verify_ssl = verify_ssl

    def get_epg(self, sport):
        """
        Loads EPG either from cache or starts fetching it

        :param sport: Cache instance
        :type sport: resources.lib.Cache
        :returns:  dict - Parsed EPG
        """
        _session = self.session.get_session()
        # check for cached epg data
        cached_epg = self.cache.get_cached_item('epg' + sport)
        if cached_epg is not None:
            return cached_epg
        return self.load_epg(sport=sport, _session=_session)

    def load_epg(self, sport, _session):
        """
        Fetches EPG & appends it to the cache

        :param sport: Chosen sport
        :type sport: string
        :param _session: Requests session instance
        :type _session: requests.session
        :returns:  dict - EPG
        """
        epg = self.fetch_epg(sport=sport, _session=_session)
        if epg.get('status') == 'success':
            page_tree = self.parse_epg(epg=epg)
            self.cache.add_cached_item('epg' + sport, page_tree)
        return page_tree

    def parse_epg(self, epg):
        """
        Parses the raw EPG

        :param epg: Raw epg
        :type epg: dict
        :returns:  dict - Parsed EPG
        """
        page_tree = {}
        data = epg.get('data', {})
        elements = data.get('elements') or data.get('data')
        use_slots = self.__use_slots(data=data)
        # iterate over every match in the epg
        for element in elements:
            # get details & metadata for the current event
            metadata = element.get('metadata', {})
            details = metadata.get('details', {})
            # get matchtime
            match_date, match_time = self.item_helper.datetime_from_utc(
                metadata=metadata,
                element=element)
            # check if we have already matches scheduled for that date
            if page_tree.get(match_date) is None:
                page_tree[match_date] = []

            matches = self.__parse_epg_element(
                use_slots=use_slots,
                element=element,
                details=details,
                match_time=match_time)

            for match in matches:
                page_tree.get(match_date).append(match)

            return page_tree

    def fetch_epg(self, sport, _session):
        """
        Builds the EPG URL & fetches the EPG

        :param sport: Chosen sport
        :type sport: string
        :param _session: Requests session instance
        :type _session: requests.session
        :returns:  dict - Parsed EPG
        """
        _epg_url = self.constants.get_epg_url()
        _epg_url += self.constants.get_sports().get(sport, {}).get('epg', '')
        return json.loads(_session.get(_epg_url).text, verify=self.verify_ssl)

    def get_stream_urls(self, video_id):
        """
        Fetches the stream urls document & parses them as well

        :param video_id: Id of the video to fetch stream urls for
        :type video_id: string
        :returns:  dict - Stream urls
        """
        stream_urls = {}
        _session = self.session.get_session()
        stream_access = json.loads(_session.post(
            self.constants.get_stream_definition_url().replace(
                '%VIDEO_ID%',
                str(video_id)),
            verify=self.verify_ssl
            ).text)
        if stream_access.get('status') == 'success':
            stream_urls['Live'] = 'https:' + \
                stream_access.get('data', {}).get(
                    'stream-access',
                    [None, None])[1]
        return stream_urls

    def get_m3u_url(self, stream_url):
        """
        Fetches the m3u description XML, parses the attributes & builds
        the m3u url

        :param stream_url: Url to fetch the m3u description XML from
        :type stream_url: string
        :returns:  string - m3u url
        """
        m3u_url = ''
        _session = self.session.get_session()
        xml_content = _session.get(stream_url, verify=self.verify_ssl)
        root = ET.fromstring(xml_content.text)
        for child in root:
            m3u_url += child.attrib.get('url', '')
            m3u_url += '?hdnea='
            m3u_url += child.attrib.get('auth', '')
        return m3u_url

    def show_sport_selection(self):
        """Creates the KODI list items for the static sport selection"""
        self.utils.log('Sport selection')
        sports = self.constants.get_sports_list()

        for sport in sports:
            url = self.utils.build_url({'for': sport})
            list_item = xbmcgui.ListItem(label=sports.get(sport).get('name'))
            list_item = self.item_helper.set_art(
                list_item=list_item,
                sport=sport)
            xbmcplugin.addDirectoryItem(
                handle=self.plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=True)
            xbmcplugin.addSortMethod(
                handle=self.plugin_handle,
                sortMethod=xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_sport_categories(self, sport):
        """
        Creates the KODI list items for the contents of a sport selection.
        It loads the sport html page & parses the event lanes given

        :param sport: Chosen sport
        :type sport: string
        """
        self.utils.log('(' + sport + ') Main Menu')
        _session = self.session.get_session()
        base_url = self.constants.get_base_url()
        sports = self.constants.get_sports_list()

        # load sport page from telekom
        url = base_url + '/' + sports.get(sport, {}).get('page')
        html = _session.get(url, verify=self.verify_ssl).text

        # parse sport page data
        events = []
        check_soup = BeautifulSoup(html, 'html.parser')
        content_groups = check_soup.find_all('div', class_='content-group')
        for content_group in content_groups:
            headline = content_group.find('h2')
            event_lane = content_group.find('event-lane')
            if headline:
                if event_lane is not None:
                    events.append((headline.get_text().encode(
                        'utf-8'), event_lane.attrs.get('prop-url')))

        # add directory item for each event
        for event in events:
            url = self.utils.build_url({'for': sport, 'lane': event[1]})
            list_item = xbmcgui.ListItem(label=self.utils.capitalize(event[0]))
            list_item = self.item_helper.set_art(
                list_item=list_item,
                sport=sport)
            xbmcplugin.addDirectoryItem(
                handle=self.plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=True)

        # Add static folder items (if available)
        # self.__add_static_folders()
        xbmcplugin.addSortMethod(
            handle=self.plugin_handle,
            sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_date_list(self, _for):
        """
        Creates the KODI list items for a list of dates with contents
        based on the current date & syndication.

        :param _for: Chosen sport
        :type _for: string
        """
        self.utils.log('Main menu')
        plugin_handle = self.plugin_handle
        addon_data = self.utils.get_addon_data()
        epg = self.get_epg(_for)
        for _date in epg.keys():
            title = ''
            items = epg.get(_date)
            for item in items:
                title = title + \
                    str(' '.join(item.get('title').replace('Uhr', '').split(
                        ' ')[:-2]).encode('utf-8')) + '\n\n'
            url = self.utils.build_url({'date': date, 'for': _for})
            list_item = xbmcgui.ListItem(label=_date)
            list_item.setProperty('fanart_image', addon_data.get('fanart'))
            list_item.setInfo('video', {
                'date': date,
                'title': title,
                'plot': title,
            })
            xbmcplugin.addDirectoryItem(
                handle=plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=True)
            xbmcplugin.addSortMethod(
                handle=plugin_handle,
                sortMethod=xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(plugin_handle)

    def show_event_lane(self, sport, lane):
        """
        Creates the KODI list items with the contents of an event-lanes
        for a selected sport & lane

        :param sport: Chosen sport
        :type sport: string
        :param lane: Chosen event-lane
        :type lane: string
        """
        self.utils.log('(' + sport + ') Lane ' + lane)
        _session = self.session.get_session()
        epg_url = self.constants.get_epg_url()
        plugin_handle = self.plugin_handle

        # load sport page from telekom
        url = epg_url + '/' + lane
        raw_data = _session.get(url, verify=self.verify_ssl).text

        # parse data
        data = json.loads(raw_data)
        data = data.get('data', [])

        # generate entries
        for item in data.get('data'):
            info = {}
            url = self.utils.build_url(
                {'for': sport, 'lane': lane, 'target': item.get('target')})
            list_item = xbmcgui.ListItem(
                label=self.item_helper.build_title(item))
            list_item = self.item_helper.set_art(list_item, sport, item)
            info['plot'] = self.item_helper.build_description(item)
            list_item.setInfo('video', info)
            xbmcplugin.addDirectoryItem(
                handle=plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=True)
        xbmcplugin.endOfDirectory(plugin_handle)

    def show_matches_list(self, game_date, _for):
        """
        Creates the KODI list items with the contents of available matches
        for a given date

        :param game_date: Chosen event-lane
        :type game_date: string
        :param _for: Chosen sport
        :type _for: string
        """
        self.utils.log('Matches list: ' + _for)
        addon_data = self.utils.get_addon_data()
        plugin_handle = self.plugin_handle
        epg = self.get_epg(_for)
        items = epg.get(game_date)
        for item in items:
            url = self.utils.build_url(
                {'hash': item.get('hash'), 'date': game_date, 'for': _for})
            list_item = xbmcgui.ListItem(label=item.get('title'))
            list_item.setProperty('fanart_image', addon_data.get('fanart'))
            xbmcplugin.addDirectoryItem(
                handle=plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=True)
            xbmcplugin.addSortMethod(
                handle=plugin_handle,
                sortMethod=xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(plugin_handle)

    def show_match_details(self, target, lane, _for):
        """
        Creates the KODI list items with the contents of a matche
        (Gamereport, Interviews, Rematch, etc.)

        :param target: Chosen match
        :type target: string
        :param lane: Chosen event-lane
        :type lane: string
        :param _for: Chosen sport
        :type _for: string
        """
        self.utils.log('Matches details')
        _session = self.session.get_session()
        epg_url = self.constants.get_epg_url()

        # load sport page from telekom
        url = epg_url + '/' + target
        raw_data = _session.get(url, verify=self.verify_ssl).text

        # parse data
        data = json.loads(raw_data)
        data = data.get('data', [])

        # check if content is available
        if data.get('content') is None:
            xbmcplugin.endOfDirectory(self.plugin_handle)
            return None

        for videos in data.get('content', []):
            vids = videos.get('group_elements', [{}])[0].get('data')
            for video in vids:
                if self.__is_playable_video_item(video=video):
                    title = video.get('title', '')
                    list_item = xbmcgui.ListItem(
                        label=title)
                    list_item = self.item_helper.set_art(
                        list_item=list_item,
                        sport=_for,
                        item=video)
                    list_item = self.__set_item_playable(
                        list_item=list_item,
                        title=title)
                    url = self.utils.build_url({
                        'for': _for,
                        'lane': lane,
                        'target': target,
                        'video_id': str(video.get('videoID'))})
                    self.__add_video_item(
                        video=video,
                        list_item=list_item,
                        url=url)
        xbmcplugin.endOfDirectory(handle=self.plugin_handle)

    def play(self, video_id):
        """
        Plays a video by Video ID

        :param target: Video ID
        :type target: string
        """
        self.utils.log('Play video: ' + str(video_id))
        use_inputstream = self.utils.use_inputstream()
        self.utils.log('Using inputstream: ' + str(use_inputstream))
        streams = self.get_stream_urls(video_id)
        for stream in streams:
            play_item = xbmcgui.ListItem(
                path=self.get_m3u_url(streams.get(stream)))
            if use_inputstream is True:
                # pylint: disable=E1101
                play_item.setContentLookup(False)
                play_item.setMimeType('application/vnd.apple.mpegurl')
                play_item.setProperty(
                    'inputstream.adaptive.stream_headers',
                    'user-agent=' + self.utils.get_user_agent())
                play_item.setProperty(
                    'inputstream.adaptive.manifest_type', 'hls')
                play_item.setProperty('inputstreamaddon',
                                      'inputstream.adaptive')
            return xbmcplugin.setResolvedUrl(
                self.plugin_handle,
                True,
                play_item)
        return False

    def __parse_regular_event(self, target_url, details, match_time):
        """
        Parses a regular event (one that´s not part of a slot)

        :param target_url: Events target url
        :type target_url: string
        :param details: Events details
        :type details: dict
        :param match_time: Events match time
        :type match_time: string
        :returns:  dict - Parsed event
        """
        return self.item_helper.build_page_leave(
            target_url=target_url,
            details=details,
            match_time=match_time)

    def __parse_slot_events(self, element, details, match_time):
        """
        Parses an event

        :param element: Raw element info
        :type element: dict
        :param details: Events details
        :type details: dict
        :param match_time: Events match time
        :type match_time: string
        :returns:  dict - Parsed event
        """
        events = []
        slots = element.get('slots')
        # get data for home and away teams
        home = details.get('home', {})
        away = details.get('away', {})
        for slot in slots:
            events = slot.get('events')
            for event in events:
                target_url = event.get('target_url', '')
                if details.get('home') is not None:
                    shorts = (
                        home.get('name_mini'),
                        away.get('name_mini'))
                    events.append(
                        self.item_helper.build_page_leave(
                            target_url=target_url,
                            details=details,
                            match_time=match_time,
                            shorts=shorts))
        return events

    def __add_static_folders(self, statics, sport):
        """
        Adds static folder items to Kodi (if available)

        :param statics: All static entries
        :type statics: dict
        :param sport: Chosen sport
        :type sport: string
        """
        if statics.get(sport):
            static_lanes = statics.get(sport)
            if static_lanes.get('categories'):
                lanes = static_lanes.get('categories')
                for lane in lanes:
                    url = self.utils.build_url({
                        'for': sport,
                        'static': True,
                        'lane': lane.get('id')})
                    list_item = xbmcgui.ListItem(label=lane.get('name'))
                    xbmcplugin.addDirectoryItem(
                        handle=self.plugin_handle,
                        url=url,
                        listitem=list_item,
                        isFolder=True)

    def __add_video_item(self, video, list_item, url):
        """
        Adds a playable video item to Kodi

        :param video: Video details
        :type video: dict
        :param list_item: Kodi list item
        :type list_item: xbmcgui.ListItem
        :param url: Video url
        :type url: string
        """
        if video.get('islivestream', True) is True:
            xbmcplugin.addDirectoryItem(
                handle=self.plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=False)

    def __parse_epg_element(self, use_slots, element, details, match_time):
        """
        Parses an EPG element & returns a list of parsed elements

        :param use_slots: Slot item
        :type use_slots: bool
        :param element: Raw EPG element
        :type element: dict
        :param details: EPG element details
        :type details: dict
        :param match_time: Events match time
        :type match_time: string
        :returns:  list - EPG element list
        """
        elements = []

        # determine event type & parse
        if use_slots is True:
            slot_events = self.__parse_slot_events(
                element=element,
                details=details,
                match_time=match_time)
            for slot_event in slot_events:
                elements.append(slot_event)
        else:
            target_url = element.get('target_url', '')
            slot = self.__parse_regular_event(
                target_url=target_url,
                details=details,
                match_time=match_time)
            elements.append(slot)
        return elements

    @classmethod
    def get_player_ids(cls, src):
        """
        Parses the player id HTML & returns stream & customer ids

        :param src: Raw HTML
        :type src: string
        :returns:  tuple - Stream & customer id
        """
        stream_id_raw = re.search('stream-id=.*', src)
        if stream_id_raw is None:
            return (None, None)
        stream_id = re.search('stream-id=.*', src).group(0).split('"')[1]
        customer_id = re.search('customer-id=.*', src).group(0).split('"')[1]
        return (stream_id, customer_id)

    @classmethod
    def __set_item_playable(cls, list_item, title):
        """
        Sets an Kodi item playable

        :param list_item: Kodi list item
        :type list_item: xbmcgui.ListItem
        :param title: Title of the video
        :type title: string
        :returns:  bool - EPG has slot type elements
        """
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {
            'title': title,
            'genre': 'Sports'})
        return list_item

    @classmethod
    def __use_slots(cls, data):
        """
        Determines if the EPG uses slot type events

        :param data: Raw EPG data
        :type data: dict
        :returns:  bool - EPG has slot type elements
        """
        if data.get('elements') is None:
            return False
        return True

    @classmethod
    def __is_playable_video_item(cls, video):
        """
        Determines if the item is playable

        :param video: Raw video data
        :type data: dict
        :returns:  bool - Video is playable
        """
        if isinstance(video, dict):
            if 'videoID' in video.keys():
                return True
        return False
