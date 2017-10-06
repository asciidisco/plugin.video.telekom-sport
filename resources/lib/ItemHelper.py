# -*- coding: utf-8 -*-
# Module: ItemHelper
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""Interface for matching API data with the Kodi item interface"""

from datetime import datetime


class ItemHelper(object):
    """Interface for matching API data with the Kodi item interface"""

    def __init__(self, constants, utils):
        """
        Injects instances

        :param constants: Constants instance
        :type constants: resources.lib.Constants
        :param utils: Utils instance
        :type utils: resources.lib.Utils
        """
        self.constants = constants
        self.utils = utils

    def build_description(self, item):
        """
        Generates an item description

        :param item: Item to be described
        :type item: dict
        :returns:  string -- Item description
        """
        desc = ''
        if item.get('metadata', {}).get('description_bold'):
            desc += item.get('metadata', {}).get('description_bold') + ' '
        if item.get('metadata', {}).get('description_regular'):
            if desc != '':
                desc += '- '
            desc += item.get('metadata', {}).get('description_regular') + ''
        if desc != '':
            desc += ':\n'
        desc += self.build_title(item) + ' '
        return desc

    def set_art(self, list_item, sport, item=None):
        """
        Sets art for the given item

        :param list_item: Kodi list item
        :type list_item: xbmcgui.ListItem
        :param sport: Chosen sport
        :type sport: string
        :param item: Item to set art for
        :type item: dict
        :returns:  xbmcgui.ListItem -- Kodi list item
        """
        sports = self.constants.get_sports_list()
        base_url = self.constants.get_base_url()
        list_item = self.__get_sports_art(
            list_item=list_item,
            sport=sport,
            sports=sports)
        if item is not None:
            metatdata = item.get('metadata', {})
            if item.get('images'):
                images = item.get('images', {})
                list_item = self.__get_editorial_art(
                    list_item=list_item,
                    base_url=base_url,
                    images=images)
            if metatdata.get('images'):
                images = metatdata.get('images')
                list_item = self.__get_editorial_art(
                    list_item=list_item,
                    base_url=base_url,
                    images=images)
        return list_item

    def build_page_leave(self, target_url, details, match_time, shorts=None):
        """
        Builds the data for an Kodi folder item

        :param target_url: Plugin target url
        :type target_url: string
        :param details: EPG element details
        :type details: dict
        :param match_time: Events match time
        :type match_time: string
        :param shorts: Add shorts desc
        :type shorts: dict
        :returns:  dict -- List item info properties
        """
        return {
            'hash': self.utils.generate_hash(target_url),
            'url': self.constants.get_base_url() + target_url,
            'title': self.build_epg_title(
                details=details,
                match_time=match_time),
            'shorts': shorts,
        }

    def build_title(self, item):
        """
        Generates an title for an item

        :param item: Item to be described
        :type item: dict
        :returns:  string -- Item title
        """
        title = ''
        metadata = item.get('metadata', {})
        if metadata.get('details') is not None:
            details = metadata.get('details')
            home = details.get('home', {})
            name_full = home.get('name_full')
            if name_full is not None:
                title += self.__build_match_title_full(details=details)
            elif name_full is None and home.get('name_short') is not None:
                title += self.__build_match_title_short(details=details)
        return self.__build_fallback_title(title=title, metadata=metadata)

    def __get_editorial_art(self, list_item, base_url, images):
        """
        Sets editorial art for the given item

        :param list_item: Kodi list item
        :type list_item: xbmcgui.ListItem
        :param base_url: Image base url
        :type base_url: string
        :param images: Map of usable images
        :type images: dict
        :returns:  xbmcgui.ListItem -- Kodi list item
        """
        image = ''
        if images.get('fallback'):
            image = base_url + '/' + images.get('fallback')
        if images.get('editorial'):
            image = base_url + '/' + images.get('editorial')
        if image != '':
            try:
                list_item.setArt({
                    'poster': image,
                    'landscape': image,
                    'thumb': image,
                    'fanart': image
                })
            except RuntimeError:
                self.utils.log('`setArt` not available')
        return list_item

    def __get_sports_art(self, list_item, sport, sports):
        """
        Sets editorial art for static sport item

        :param list_item: Kodi list item
        :type list_item: xbmcgui.ListItem
        :param sport: Chosen sport
        :type sport: string
        :param sports: Map of available sports
        :type sports: dict
        :returns:  xbmcgui.ListItem -- Kodi list item
        """
        try:
            list_item.setArt({
                'poster': sports.get(sport).get('fanart'),
                'landscape': sports.get(sport).get('fanart'),
                'thumb': sports.get(sport).get('image'),
                'fanart': sports.get(sport).get('fanart')
            })
        except RuntimeError:
            self.utils.log('`setArt` not available')
        return list_item

    @classmethod
    def __build_fallback_title(cls, title, metadata):
        """
        Generates a fallback title

        :param title: Original title
        :type title: string
        :param metadata: Item metadata
        :type metadata: dict
        :returns:  string -- Fallback title
        """
        fallback_title = ''
        if title != '':
            return title
        fallback_title += metadata.get('title', '')
        if fallback_title == '':
            fallback_title += metadata.get('description_regular', '')
        if fallback_title == '':
            fallback_title += metadata.get('description_bold', '')
        return fallback_title

    @classmethod
    def __build_match_title_short(cls, details):
        """
        Generates a short match title

        :param details: Item details
        :type details: dict
        :returns:  string -- Match title (short)
        """
        title = details.get('home', {}).get('name_short')
        title += ' - '
        title += details.get('away', {}).get('name_short')
        return title

    @classmethod
    def __build_match_title_full(cls, details):
        """
        Generates a long match title

        :param details: Item details
        :type details: dict
        :returns:  string -- Match title (long)
        """
        title = details.get('home', {}).get('name_full')
        title += ' - '
        title += details.get('away', {}).get('name_full')
        return title

    @classmethod
    def build_epg_title(cls, details, match_time):
        """
        Generates a epg title

        :param details: Item details
        :type details: dict
        :param match_time: Events match time
        :type match_time: string
        :returns:  string -- EPG item title
        """
        title = details.get('home', {}).get('name_full', '')
        title += ' - '
        title += details.get('away', {}).get('name_full', '')
        title += ' (' + match_time + ' Uhr)'
        return title

    @classmethod
    def datetime_from_utc(cls, metadata, element=None):
        """
        Generates a homan readable time from an items UTC timestamp

        :param metadata: Item metadata
        :type metadata: dict
        :param details: Item details
        :type details: dict
        :returns:  tuple -- Match date & match time
        """
        date_container = None
        if metadata.get('scheduled_start'):
            date_container = metadata.get('scheduled_start', {})
        elif element is not None:
            date_container = element.get('scheduled_start', {})
        if date_container is None:
            return (None, None)
        timestamp = float(date_container.get('date'))
        match_datetime = datetime.fromtimestamp(timestamp)
        match_date = match_datetime.strftime('%d.%m.%Y')
        match_time = match_datetime.strftime('%H:%M')
        return (match_date, match_time)
