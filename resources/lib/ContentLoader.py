# -*- coding: utf-8 -*-
# Module: ContentLoader
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""ADD ME"""

import re
import json
import xml.etree.ElementTree as ET
from datetime import date
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup


class ContentLoader(object):
    """ADD ME"""

    def __init__(self, cache, session, item_helper, handle):
        self.constants = session.constants
        self.utils = session.utils
        self.cache = cache
        self.session = session
        self.item_helper = item_helper
        self.plugin_handle = handle

    def get_epg(self, _for):
        """ADD ME"""
        _session = self.session.get_session()
        # check for cached epg data
        cached_epg = self.cache.get_cached_item('epg' + _for)
        if cached_epg is not None:
            return cached_epg
        return self.load_epg(_for=_for, _session=_session)

    def load_epg(self, _for, _session):
        """ADD ME"""
        epg = self.fetch_epg(_for=_for, _session=_session)
        if epg.get('status') == 'success':
            page_tree = self.parse_epg(epg=epg)
            self.cache.add_cached_item('epg' + _for, page_tree)
        return page_tree

    def parse_epg(self, epg):
        """ADD ME"""
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
            # determine event type & parse
            if use_slots is True:
                slot_events = self.__parse_slot_events(
                    element=element,
                    details=details,
                    match_time=match_time)
                for slot_event in slot_events:
                    page_tree[match_date].append(slot_event)
            else:
                target_url = element.get('target_url', '')
                page_tree.get(match_date).append(
                    self.__parse_regular_event(
                        target_url=target_url,
                        details=details,
                        match_time=match_time))
            return page_tree

    def fetch_epg(self, _for, _session):
        """ADD ME"""
        _epg_url = self.constants.get_epg_url()
        _epg_url += self.constants.get_sports().get(_for, {}).get('epg', '')
        return json.loads(_session.get(_epg_url).text)

    @classmethod
    def get_player_ids(cls, src):
        """ADD ME"""
        stream_id_raw = re.search('stream-id=.*', src)
        if stream_id_raw is None:
            return (None, None)
        stream_id = re.search('stream-id=.*', src).group(0).split('"')[1]
        customer_id = re.search('customer-id=.*', src).group(0).split('"')[1]
        return (stream_id, customer_id)

    def get_stream_urls(self, video_id):
        """ADD ME"""
        stream_urls = {}
        _session = self.session.get_session()
        stream_access = json.loads(_session.post(
            self.constants.get_stream_definition_url().replace(
                '%VIDEO_ID%',
                str(video_id))
            ).text)
        if stream_access.get('status') == 'success':
            stream_urls['Live'] = 'https:' + \
                stream_access.get('data').get('stream-access')[1]
        return stream_urls

    def get_m3u_url(self, stream_url):
        """ADD ME"""
        m3u_url = ''
        _session = self.session.get_session()
        root = ET.fromstring(_session.get(stream_url).text)
        for child in root:
            m3u_url = child.attrib.get(
                'url') + '?hdnea=' + child.attrib.get('auth')
        return m3u_url

    def show_sport_selection(self):
        """ADD ME"""
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
        """ADD ME"""
        self.utils.log('(' + sport + ') Main Menu')
        _session = self.session.get_session()
        base_url = self.constants.get_base_url()
        sports = self.constants.get_sports_list()

        # load sport page from telekom
        url = base_url + '/' + sports.get(sport, {}).get('page')
        html = _session.get(url).text

        # parse sport page data
        events = []
        check_soup = BeautifulSoup(html, 'html.parser')
        content_groups = check_soup.find_all('div', class_='content-group')
        for content_group in content_groups:
            headline = content_group.find('h2')
            event_lane = content_group.find('event-lane')
            if headline:
                events.append((headline.get_text().encode(
                    'utf-8'), event_lane.attrs.get('prop-url')))

        for event in events:
            url = self.utils.build_url({'for': sport, 'lane': event[1]})
            list_item = xbmcgui.ListItem(label=self.utils.capitalize(event[0]))
            try:
                list_item.setArt({
                    'poster': sports.get(sport, {}).get('image'),
                    'landscape': sports.get(sport, {}).get('image'),
                    'thumb': sports.get(sport, {}).get('image'),
                    'fanart': sports.get(sport, {}).get('image')
                })
            except RuntimeError:
                self.utils.log('`setArt` not available')
            xbmcplugin.addDirectoryItem(
                handle=self.plugin_handle,
                url=url,
                listitem=list_item,
                isFolder=True)

        # add static folder items (if available)
        # if statics.get(sport):
        #    static_lanes = statics.get(sport)
        #    if static_lanes.get('categories'):
        #        lanes = static_lanes.get('categories')
        #        for lane in lanes:
        #            url = build_url(
        # {'for': sport, 'static': True, 'lane': lane.get('id')})
        #            li = xbmcgui.ListItem(label=lane.get('name'))
        #            li.setProperty('fanart_image', addon_data.get('fanart'))
        #            xbmcplugin.addDirectoryItem(
        # handle=plugin_handle,
        # url=url,
        # listitem=li,
        # isFolder=True)

        xbmcplugin.addSortMethod(
            handle=self.plugin_handle,
            sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def show_date_list(self, _for):
        """ADD ME"""
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
        """ADD ME"""
        self.utils.log('(' + sport + ') Lane ' + lane)
        _session = self.session.get_session()
        epg_url = self.constants.get_epg_url()
        plugin_handle = self.plugin_handle

        # load sport page from telekom
        url = epg_url + '/' + lane
        raw_data = _session.get(url).text

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
        """ADD ME"""
        self.utils.log('Matches list')
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
        """ADD ME"""
        self.utils.log('Matches details')
        plugin_handle = self.plugin_handle
        _session = self.session.get_session()
        epg_url = self.constants.get_epg_url()
        # load sport page from telekom
        url = epg_url + '/' + target
        raw_data = _session.get(url).text

        # parse data
        data = json.loads(raw_data)
        data = data.get('data', [])

        if data.get('content'):
            for videos in data.get('content', []):
                vids = videos.get('group_elements', [{}])[0].get('data')
                for video in vids:
                    if isinstance(video, dict):
                        if 'videoID' in video.keys():
                            list_item = xbmcgui.ListItem(
                                label=video.get('title'))
                            list_item = self.item_helper.set_art(
                                list_item,
                                _for,
                                video)
                            list_item.setProperty('IsPlayable', 'true')
                            is_livestream = 'False'
                            if video.get('islivestream', False) is True:
                                is_livestream = 'True'
                            url = self.utils.build_url({
                                'for': _for,
                                'lane': lane,
                                'target': target,
                                'is_livestream': is_livestream,
                                'video_id': str(video.get('videoID'))})

                            xbmcplugin.addDirectoryItem(
                                handle=plugin_handle,
                                url=url,
                                listitem=list_item,
                                isFolder=False)
        xbmcplugin.endOfDirectory(plugin_handle)

    def play(self, video_id):
        """ADD ME"""
        self.utils.log('Play video: ' + str(video_id))
        use_inputstream = self.utils.use_inputstream()
        self.utils.log('Using inputstream: ' + str(use_inputstream))
        streams = self.get_stream_urls(video_id)
        for stream in streams:
            play_item = xbmcgui.ListItem(
                path=self.get_m3u_url(streams.get(stream)))
            if use_inputstream is True:
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
        """ADD ME"""
        return self.item_helper.build_page_leave(
            target_url=target_url,
            details=details,
            match_time=match_time)

    def __parse_slot_events(self, element, details, match_time):
        """ADD ME"""
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

    @classmethod
    def __use_slots(cls, data):
        """ADD ME"""
        if data.get('elements') is None:
            return False
        return True
