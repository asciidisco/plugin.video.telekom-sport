"""ADD ME"""

import urllib
import json
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
import xbmcplugin
import xbmcgui
from bs4 import BeautifulSoup

class ContentLoader(object):
    """ADD ME"""

    def __init__(self, constants, utils, cache, session, item_helper, plugin_handle):
        self.constants = constants
        self.utils = utils
        self.cache = cache
        self.session = session
        self.item_helper = item_helper
        self.plugin_handle = plugin_handle  

    def get_epg(self, _for):
        """ADD ME"""
        _session = self.session.get_session()
        # check for cached epg data
        cached_epg = self.cache.get_cached_item('epg' + _for)
        _epg_url = self.constants.get_epg_url() + self.constants.get_sports().get(_for).get('epg')
        if cached_epg is not None:
            return cached_epg
        page_tree = {}
        epg = json.loads(_session.get(_epg_url).text)
        use_slots = True
        if epg.get('status') == 'success':
            elements = epg.get('data').get('elements')
            if elements is None:
                elements = epg.get('data').get('data')
                use_slots = False
            for element in elements:
                if use_slots is True:
                    element_date = date.fromtimestamp(float(element.get('date').get('utc_timestamp'))).strftime('%d.%m.%Y')
                    if page_tree.get(element_date) is None:
                        page_tree[element_date] = []
                    slots = element.get('slots')
                    for slot in slots:
                        events = slot.get('events')
                        for event in events:
                            if event.get('metadata', {}).get('details', {}).get('home') is not None:
                                page_tree.get(element_date).append({
                                    'hash': self.utils.generate_hash(event.get('target_url')),
                                    'url': self.constants.get_base_url() + event.get('target_url'),
                                    'title': event.get('metadata').get('details').get('home').get('name_full') + ' - ' + event.get('metadata').get('details').get('away').get('name_full') + ' (' + datetime.fromtimestamp(float(event.get('metadata').get('scheduled_start').get('utc_timestamp'))).strftime('%H:%M') + ' Uhr)',
                                    'shorts': (event.get('metadata').get('details').get('home').get('name_mini'), event.get('metadata').get('details').get('away').get('name_mini')),
                                })
                else:
                    element_date = date.fromtimestamp(float(element.get('metadata').get('scheduled_start').get('utc_timestamp'))).strftime('%d.%m.%Y')
                    if page_tree.get(element_date) is None:
                        page_tree[element_date] = []
                    title = element.get('metadata').get('title', '')
                    if title == '':
                        title = element.get('metadata').get('details').get('home').get('name_full') + ' - ' + element.get('metadata').get('details').get('away').get('name_full') + ' (' + datetime.fromtimestamp(float(element.get('metadata').get('scheduled_start').get('utc_timestamp'))).strftime('%H:%M') + ' Uhr)'
                    page_tree.get(element_date).append({
                        'hash': self.utils.generate_hash(element.get('target_url')),
                        'url': self.constants.get_base_url() + element.get('target_url'),
                        'title': title,
                        'shorts': None,
                    })
        self.cache.add_cached_item('epg' + _for, page_tree)
        return page_tree

    @classmethod
    def get_player_ids(cls, src):
        """ADD ME"""
        stream_id = re.search('stream-id=.*', src)
        if stream_id is None:
            return (None, None)
        return (re.search('stream-id=.*', src).group(0).split('"')[1], re.search('customer-id=.*', src).group(0).split('"')[1])

    def get_stream_urls(self, video_id):
        """ADD ME"""
        stream_urls = {}
        _session = self.session.get_session()
        stream_access = json.loads(_session.post(self.constants.get_stream_definition_url().replace('%VIDEO_ID%', str(video_id))).text)
        if stream_access.get('status') == 'success':
            stream_urls['Live'] = 'https:' + stream_access.get('data').get('stream-access')[1]
        return stream_urls

    def get_m3u_url(self, stream_url):
        """ADD ME"""
        m3u_url = ''
        _session = self.session.get_session()
        root = ET.fromstring(_session.get(stream_url).text)
        for child in root:
            m3u_url = child.attrib.get('url') + '?hdnea=' + child.attrib.get('auth')
        return m3u_url

    def show_sport_selection(self):
        """ADD ME"""
        self.utils.log('Sport selection')
        addon_data = self.utils.get_addon_data()
        sports = self.constants.get_sports_list()
        plugin_handle = self.plugin_handle
        for sport in sports:
            url = self.utils.build_url({'for': sport})
            li = xbmcgui.ListItem(label=sports.get(sport).get('name'))
            li.setProperty('fanart_image', addon_data.get('fanart'))
            try:
                li.setArt({
                    'poster': sports.get(sport).get('image'),
                    'landscape': sports.get(sport).get('image'),
                    'thumb': sports.get(sport).get('image'),
                    'fanart': sports.get(sport).get('image')
                })
            except Exception as e:
                self.utils.log('Kodi version does not implement setArt')
            xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
            xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(plugin_handle)    

    def show_sport_categories(self, sport):
        """ADD ME"""
        self.utils.log('(' + sport + ') Main Menu')
        _session = self.session.get_session()
        addon_data = self.utils.get_addon_data()
        base_url = self.constants.get_base_url()
        sports = self.constants.get_sports_list()
        plugin_handle = self.plugin_handle

        # load sport page from telekom
        url = base_url + '/' + sports.get(sport, {}).get('page')
        html = _session.get(url).text

        # parse sport page data
        events = []
        check_soup = BeautifulSoup(html, 'html.parser')
        content_groups = check_soup.find_all('div', class_='content-group')
        for content_group in content_groups:
            headline = content_group.find('h2')
            eventLane = content_group.find('event-lane')
            if headline:
                events.append((headline.get_text().encode('utf-8'), eventLane.attrs.get('prop-url')))

        for event in events:
            url = self.utils.build_url({'for': sport, 'lane': event[1]})
            li = xbmcgui.ListItem(label=self.utils.capitalize(event[0]))
            li.setProperty('fanart_image', addon_data.get('fanart'))
            try:
                li.setArt({
                    'poster': sports.get(sport).get('image'),
                    'landscape': sports.get(sport).get('image'),
                    'thumb': sports.get(sport).get('image'),
                    'fanart': sports.get(sport).get('image')
                })
            except Exception as e:
                self.utils.log('Kodi version does not implement setArt')
            xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
            
        # add static folder items (if available)
        #if statics.get(sport):
        #    static_lanes = statics.get(sport)
        #    if static_lanes.get('categories'):
        #        lanes = static_lanes.get('categories')
        #        for lane in lanes:
        #            url = build_url({'for': sport, 'static': True, 'lane': lane.get('id')})
        #            li = xbmcgui.ListItem(label=lane.get('name'))
        #            li.setProperty('fanart_image', addon_data.get('fanart'))
        #            xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
                    
        xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(plugin_handle)  

    def show_date_list(self, _for):
        """ADD ME"""
        self.utils.log('Main menu')
        plugin_handle = self.plugin_handle
        addon_data = self.utils.get_addon_data()
        epg = self.get_epg(_for)
        for date in epg.keys():
            title = ''
            items = epg.get(date)
            for item in items:
                title = title + str(' '.join(item.get('title').replace('Uhr', '').split(' ')[:-2]).encode('utf-8')) + '\n\n'
            url = self.utils.build_url({'date': date, 'for': _for})
            li = xbmcgui.ListItem(label=date)
            li.setProperty('fanart_image', addon_data.get('fanart'))
            li.setInfo('video', {
                'date': date,
                'title': title,
                'plot': title,
            })
            xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
            xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(plugin_handle)

    def show_event_lane(self, sport, lane):
        """ADD ME"""
        self.utils.log('(' + sport + ') Lane ' + lane)
        addon_data = self.utils.get_addon_data()
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
            url = self.utils.build_url({'for': sport, 'lane': lane, 'target': item.get('target')})
            li = xbmcgui.ListItem(label=self.item_helper.build_title(item))
            li = self.item_helper.set_art(li, sport, item)
            info['plot'] = self.item_helper.build_description(item)
            li.setInfo('video', info)
            xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(plugin_handle)  

    def show_matches_list(self, game_date, _for):
        """ADD ME"""
        self.utils.log('Matches list')
        addon_data = self.utils.get_addon_data()
        plugin_handle = self.plugin_handle
        epg = self.get_epg(_for)
        date = epg.get(game_date)
        for item in date:
            url = self.utils.build_url({'hash': item.get('hash'), 'date': game_date, 'for': _for})
            li = xbmcgui.ListItem(label=item.get('title'))
            li.setProperty('fanart_image', addon_data.get('fanart'))        
            xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
            xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE)
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
                        if type(video) is dict:
                            if 'videoID' in video.keys() and 'video_type' in video.keys():
                                li = xbmcgui.ListItem(label=video.get('title'))
                                li = self.item_helper.set_art(li, _for, video)
                                li.setProperty('IsPlayable', 'true')
                                is_livestream = 'False'
                                if video.get('islivestream', False) is True:
                                    is_livestream = 'True'
                                url = self.utils.build_url({'for': _for, 'lane': lane, 'target': target, 'is_livestream': is_livestream, 'video_id': str(video.get('videoID'))})
                                xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(plugin_handle)

    def play(self, video_id):
        """ADD ME"""
        self.utils.log('Play video: ' + str(video_id))
        use_inputstream = self.utils.use_inputstream()
        self.utils.log('Using inputstream: ' + str(use_inputstream))
        streams = self.get_stream_urls(video_id)
        for stream in streams:
            play_item = xbmcgui.ListItem(path=self.get_m3u_url(streams.get(stream)))
            if use_inputstream is True:
                play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            return xbmcplugin.setResolvedUrl(self.plugin_handle, True, play_item)
        return False
