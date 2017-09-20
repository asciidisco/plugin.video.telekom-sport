"""ADD ME"""

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
      
    def set_art(self, li, sport, item=None):
        """ADD ME"""
        addon_data = self.utils.get_addon_data()
        sports = self.constants.get_sports_list()
        base_url = self.constants.get_base_url()
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
                        li.setArt({
                            'poster': image,
                            'landscape': image,
                            'thumb': image,
                            'fanart': image
                        })
                    except Exception as e:
                        self.utils.log('Kodi version does not implement setArt')            
            if item.get('metadata', {}).get('images'):
                images = item.get('metadata', {}).get('images')
                image = ''
                if images.get('fallback'):
                    image = base_url + '/' + images.get('fallback')                
                if images.get('editorial'):
                    image = base_url + '/' + images.get('editorial')
                if image != '':
                    try:
                        li.setArt({
                            'poster': image,
                            'landscape': image,
                            'thumb': image,
                            'fanart': image
                        })
                    except Exception as e:
                        self.utils.log('Kodi version does not implement setArt')
        return li 

    @classmethod
    def build_title(cls, item):
        """ADD ME"""
        title = ''
        metadata = item.get('metadata')
        if (metadata.get('details')):
            if (metadata.get('details', {}).get('home', {}).get('name_full')):
                title += metadata.get('details', {}).get('home', {}).get('name_full')
                title += ' - '
                title += metadata.get('details', {}).get('away', {}).get('name_full')
            else:
                if (metadata.get('details', {}).get('home', {}).get('name_short')):
                    title += metadata.get('details', {}).get('home', {}).get('name_short')
                    title += ' - '
                    title += metadata.get('details', {}).get('away', {}).get('name_short')
        if title == '':
            title = metadata.get('title', '')
        if title == '':
            title = metadata.get('description_regular', '')
        if title == '':
            title = metadata.get('description_bold', '')
        return title
