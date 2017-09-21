# -*- coding: utf-8 -*-
# Module: ItemHelper
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""ADD ME"""

from datetime import datetime


class ItemHelper(object):
    """ADD ME"""

    def __init__(self, constants, utils):
        """ADD ME"""
        self.constants = constants
        self.utils = utils

    def build_description(self, item):
        """ADD ME"""
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
        """ADD ME"""
        addon_data = self.utils.get_addon_data()
        sports = self.constants.get_sports_list()
        base_url = self.constants.get_base_url()
        list_item.setProperty('fanart_image', addon_data.get('fanart'))
        try:
            list_item.setArt({
                'poster': sports.get(sport).get('image'),
                'landscape': sports.get(sport).get('image'),
                'thumb': sports.get(sport).get('image'),
                'fanart': sports.get(sport).get('image')
            })
        except RuntimeError:
            self.utils.log('`setArt` not available')
        if item is not None:
            if item.get('images'):
                images = item.get('images', {})
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
            if item.get('metadata', {}).get('images'):
                images = item.get('metadata', {}).get('images')
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

    def build_page_leave(self, target_url, details, match_time, shorts=None):
        """ADD ME"""
        return {
            'hash': self.utils.generate_hash(target_url),
            'url': self.constants.get_base_url() + target_url,
            'title': self.build_epg_title(
                details=details,
                match_time=match_time),
            'shorts': shorts,
        }

    @classmethod
    def build_title(cls, item):
        """ADD ME"""
        title = ''
        metadata = item.get('metadata')
        if metadata.get('details') is not None:
            if metadata.get('details').get('home', {}).get('name_full'):
                details = metadata.get('details')
                title += details.get('home', {}).get('name_full')
                title += ' - '
                title += details.get('away', {}).get('name_full')
            else:
                if metadata.get('details').get('home', {}).get('name_short'):
                    details = metadata.get('details')
                    title += details.get('home', {}).get('name_short')
                    title += ' - '
                    title += details.get('away', {}).get('name_short')
        if title == '':
            title = metadata.get('title', '')
        if title == '':
            title = metadata.get('description_regular', '')
        if title == '':
            title = metadata.get('description_bold', '')
        return title

    @classmethod
    def build_epg_title(cls, details, match_time):
        """ADD ME"""
        title = details.get('home', {}).get('name_full', '')
        title += ' - '
        title += details.get('away', {}).get('name_full', '')
        title += ' (' + match_time + ' Uhr)'
        return title

    @classmethod
    def datetime_from_utc(cls, metadata, element=None):
        """ADD ME"""
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
