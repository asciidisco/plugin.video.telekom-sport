#!/usr/bin/env python
# coding: utf8
from __future__ import unicode_literals
try:
   import cPickle as pickle
except:
   import pickle
import hashlib
import urllib2
import urllib
import base64
import random
import string
import uuid
import json
import time
import sys
import re
import md5
import xml.etree.ElementTree as ET
from datetime import date, datetime
from cookielib import CookieJar
from urlparse import parse_qsl
from os import path, remove

import xbmcplugin
import xbmcaddon
import xbmcvfs
import xbmcgui
import xbmc

from bs4 import BeautifulSoup


# urls for login & data retrival
base_url = 'https://www.telekomsport.de'
login_link = base_url + '/service/auth/web/login?headto=https://www.telekomsport.de/info'
login_endpoint = 'https://accounts.login.idm.telekom.com/sso'
epg_url = base_url + '/api/v1/'
stream_definition_url = base_url + '/service/player/streamAccess?videoId=%VIDEO_ID%&label=2780_hls'

# core event types
sports = {
    'liga3': {
        'image': 'https://www.telekomsport.de/images/packete/3liga.png',
        'name': '3. Liga',
        'indicators': ['3. Liga'],
        'page': 'fussball/3-liga',
    },
    'del': {
        'image': 'https://www.telekomsport.de/images/packete/del.png',
        'name': 'Deutsche Eishockey Liga',
        'indicators': [''],
        'page': 'eishockey/del',
    },
    'ffb': {
        'image': 'https://www.telekomsport.de/images/packete/frauenbundesliga.png',
        'name': 'Frauen-Bundesliga',
        'indicators': [''],
        'page': 'fussball/frauen-bundesliga',
    },
    'fcb': {
        'image': 'https://www.telekomsport.de/images/packete/fcbayerntv.png',
        'name': 'FC Bayern.TV',
        'indicators': [''],
        'page': 'fc-bayern-tv-live',
    },
    'bbl': {
        'image': 'https://www.telekomsport.de/images/packete/easyCredit.png',
        'name': 'Easycredit BBL',
        'indicators': [''],
        'page': 'basketball/bbl',
    },   
    'bel': {
        'image': 'https://www.telekomsport.de/images/packete/euroleague.png',
        'name': 'Basketball Turkish Airlines Euroleague',
        'indicators': [''],
        'page': 'basketball/euroleague',
    },
    'eurobasket': {
        'image': 'http://www.fiba.basketball/img/12104_logo_landscape.png',
        'name': 'FIBA Eurobasket',
        'indicators': [''],
        'page': 'basketball/eurobasket2017',
    },    
    'skybuli': {
        'image': 'https://www.telekomsport.de/images/packete/sky-bundesliga.png',
        'name': 'Sky Fußball Bundesliga',
        'indicators': [''],
        'page': 'sky/bundesliga',
    },
    'skychamp': {
        'image': 'https://www.telekomsport.de/images/packete/sky-cl.png',
        'name': 'Sky Champions League',
        'indicators': [''],
        'page': 'sky/champions-league',
    },           
    'skyhandball': {
        'image': 'https://www.telekomsport.de/images/packete/DKB.png',
        'name': 'Handball Bundesliga',
        'indicators': [''],
        'page': 'sky/handball-bundesliga',
    },           
}

# setup plugin base stuff
plugin_handle = int(sys.argv[1])
kodi_base_url = sys.argv[0]

def encode(data):
    enc = []
    key = getmac()    
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode(''.join(enc))

def decode(data):
    dec = []
    key = getmac()
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return ''.join(dec)

def getmac():
    mac = uuid.getnode()
    if (mac >> 40) % 2:
        mac = node()
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(mac)).bytes

def login(_session, user, password):
    payload = {}
    addon_data = get_addon_data()
    # check if the suer is already logged in
    check_res = _session.get(base_url)
    check_soup = BeautifulSoup(check_res.text, 'html.parser')
    if check_soup.find('a', class_='logout') is not None:
        return True
    # clear session
    clear_session()
    _session = get_session()
    # get contents of login page
    res = _session.get(login_link)
    login_page_html = res.text
    soup = BeautifulSoup(login_page_html, 'html.parser')
    # find all <input/> items in the login form & grep their data
    for item in soup.find(id='login').find_all('input'):
        if item.attrs.get('name', None) is not None:
            payload[item.attrs.get('name', None)] = item.attrs.get('value', '')
    # overwrite user & password fields with our settings data
    payload['pw_usr'] = decode(user)
    payload['pw_pwd'] = decode(password)
    # persist the session
    #payload['persist_session'] = 1
    # add empyt sumbit field (it is the value of the button in the page...)
    payload['pw_submit'] = ''
    # do the login & read the incoming html <title/> 
    # attribute to determine of the login was successfull
    login_res = _session.post(login_endpoint, data=payload)
    soup = BeautifulSoup(login_res.text, 'html.parser')
    success = 'Sport' in soup.find('title').get_text()
    if success:
        save_session(_session, addon_data.get('cookie_path'))
        return True
    else:
        return False

def get_epg(_session, _for):
    # check for cached epg data
    cached_epg = get_cached_item('epg' + _for)
    _epg_url = epg_url + sports.get(_for).get('epg')
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
                                'hash': generateHash(event.get('target_url')),
                                'url': base_url + event.get('target_url'),
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
                    'hash': generateHash(element.get('target_url')),
                    'url': base_url + element.get('target_url'),
                    'title': title,
                    'shorts': None,
                })
    add_cached_item('epg' + _for, page_tree)
    return page_tree

def get_addon():
    return xbmcaddon.Addon()

def show_password_dialog():
    dlg = xbmcgui.Dialog()
    return dlg.input(get_local_string(string_id=32004), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)

def show_email_dialog():
    dlg = xbmcgui.Dialog()
    return dlg.input(get_local_string(string_id=32005), type=xbmcgui.INPUT_ALPHANUM)

def show_not_available_dialog():
    addon_data = get_addon_data()
    dlg = xbmcgui.Dialog()
    return dlg.ok(addon_data.get('plugin'), get_local_string(string_id=32009))

def show_login_failed_notification():
    dialog = xbmcgui.Dialog()
    dialog.notification(get_local_string(string_id=32006), get_local_string(string_id=32007), xbmcgui.NOTIFICATION_ERROR, 5000)

def get_addon_data():
    addon = get_addon()
    base_data_path = xbmc.translatePath(addon.getAddonInfo('profile'))
    return dict(
        plugin = addon.getAddonInfo('name'),
        version = addon.getAddonInfo('version'),
        fanart = addon.getAddonInfo('fanart'),
        base_data_path = base_data_path,
        cookie_path = base_data_path + 'COOKIE'
    )

def log(msg, level=xbmc.LOGNOTICE):
    addon_data = get_addon_data()
    xbmc.log('[' + addon_data.get('plugin') + '] ' + str(msg), level)

def get_local_string(string_id):
    src = xbmc if string_id < 30000 else get_addon()
    locString = src.getLocalizedString(string_id)
    if isinstance(locString, unicode):
        locString = locString.encode('utf-8')
    return locString    

def build_url(query):
    return kodi_base_url + '?' + urllib.urlencode(query)

def setup_memcache():
    cached_items = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('memcache')
    if len(cached_items) < 1:
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty('memcache', pickle.dumps({}))

def has_cached_item(cache_id):
    cached_items = pickle.loads(xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('memcache'))
    return cache_id in cached_items.keys()

def get_cached_item(cache_id):
    cached_items = pickle.loads(xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('memcache'))
    if has_cached_item(cache_id) is not True:
        return None
    return cached_items[cache_id]

def add_cached_item(cache_id, contents):
    cached_items = pickle.loads(xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('memcache'))
    cached_items.update({cache_id: contents})
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty('memcache', pickle.dumps(cached_items))

def get_kodi_version():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = json.loads(json_query)
    version_installed = 17
    if json_query.get('result', {}).has_key('version'):
        version_installed  = json_query['result']['version'].get('major', 17)
    return version_installed

def get_inputstream_version():
    # construct the payload
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

def show_sport_selection():
    log('Sport selection')
    addon_data = get_addon_data()
    for sport in sports:
        url = build_url({'for': sport})
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
            log('Kodi version does not implement setArt')
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
        xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.endOfDirectory(plugin_handle)    

def has_credentials(user, password):
    return user != '' or password != ''

def set_credentials():
    raw_user = show_email_dialog()
    raw_password = show_password_dialog()
    user = encode(raw_user)
    password = encode(raw_password)
    addon.setSetting('email', user)
    addon.setSetting('password', password)
    return (user, password)

def logout():
    clear_session()

def switch_account():
    clear_session()
    set_credentials()

"""def router(paramstring, _session, user, password, use_inputstream):
    params = dict(parse_qsl(paramstring))
    keys = params.keys()
    if params.get('action', None) is not None:
        if params.get('action', None) == 'logout':
            logout()
        else:
            switch_account()
        return True
    if login(_session, user, password) is True:
        if len(keys) == 0:
            show_sport_selection()
            return True
        if params.get('stream', None) is not None:
            play(_session, params.get('stream', None), params.get('hash', None), params.get('date', None), params.get('for', None), use_inputstream)
            return True   
        if params.get('hash', None) is not None:
            show_match_details(_session, params.get('hash', None), params.get('date', None), params.get('for', None))
            return True    
        if params.get('date', None) is not None:
            show_matches_list(_session, params.get('date', None), params.get('for', None))
            return True
        if params.get('for', None) is not None:
            show_date_list(_session, params.get('for', None))
            return True        
    else:
        show_login_failed_notification()"""

def capitalize(sentence):
    cap = ''
    words = sentence.decode('utf-8').split(' ')
    for word in words:
        cap += word[:1].upper() + word[1:].lower()
        cap += ' '
    return cap.encode('utf-8')

def show_sport_categories(sport):
    log('(' + sport + ') Main Menu')
    addon_data = get_addon_data()

    # load sport page from telekom
    url = base_url + '/' + sports.get(sport, {}).get('page')
    response = urllib2.urlopen(url)
    html = response.read()
    response.close()

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
        url = build_url({'for': sport, 'lane': event[1]})
        li = xbmcgui.ListItem(label=capitalize(event[0]))
        li.setProperty('fanart_image', addon_data.get('fanart'))
        try:
            li.setArt({
                'poster': sports.get(sport).get('image'),
                'landscape': sports.get(sport).get('image'),
                'thumb': sports.get(sport).get('image'),
                'fanart': sports.get(sport).get('image')
            })
        except Exception as e:
            log('Kodi version does not implement setArt')
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
        xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.endOfDirectory(plugin_handle)  

def show_event_lane(sport, lane):
    log('(' + sport + ') Lane ' + lane)
    addon_data = get_addon_data()

    # load sport page from telekom
    url = epg_url + '/' + lane
    response = urllib2.urlopen(url)
    raw_data = response.read()
    response.close()
    
    # parse data
    data = json.loads(raw_data)
    data = data.get('data', [])

    # generate entries
    for item in data.get('data'):
        info = {}
        url = build_url({'for': sport, 'lane': lane, 'target': item.get('target')})
        li = xbmcgui.ListItem(label=build_title(item))
        li = set_art(li, sport, item)
        info['plot'] = build_description(item)
        li.setInfo('video', info)
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(plugin_handle)  

def build_description(item):
    desc = ''
    if item.get('metadata', {}).get('description_bold'):
        desc += item.get('metadata', {}).get('description_bold') + ' '
    if item.get('metadata', {}).get('description_regular'):
        if desc != '':
            desc += '- '
        desc += item.get('metadata', {}).get('description_regular') + ''
    if desc != '':
        desc += ':\n'
    desc += build_title(item) + ' '

    return desc

def build_title(item):
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
    
def set_art(li, sport, item=None):
    li.setProperty('fanart_image', addon_data.get('fanart'))
    try:
        li.setArt({
            'poster': sports.get(sport).get('image'),
            'landscape': sports.get(sport).get('image'),
            'thumb': sports.get(sport).get('image'),
            'fanart': sports.get(sport).get('image')
        })
    except Exception as e:
        log('Kodi version does not implement setArt')
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
                    log('Kodi version does not implement setArt')            
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
                    log('Kodi version does not implement setArt')
    return li 

def show_event_details(sport, lane, target):
    log('(' + sport + ') Lane ' + lane + ' Target ' + target)
    addon_data = get_addon_data()

    # load sport page from telekom
    url = epg_url + '/' + target
    response = urllib2.urlopen(url)
    raw_data = response.read()
    response.close()
    
    # parse data
    data = json.loads(raw_data)
    data = data.get('data', [])

    if data.get('content'):
        for videos in data.get('content', []):
            vids = videos.get('group_elements', [{}])[0].get('data')
            for video in vids:
                if type(video) is dict:
                    if 'videoID' in video.keys() and 'video_type' in video.keys():
                        log(json.dumps(video))
                        li = xbmcgui.ListItem(label=video.get('title'))
                        li = set_art(li, sport, video)
                        li.setProperty('IsPlayable', 'true')
                        is_livestream = 'False'
                        if video.get('islivestream', False) is True:
                            is_livestream = 'True'
                        url = build_url({'for': sport, 'lane': lane, 'target': target, 'is_livestream': is_livestream, 'video_id': str(video.get('videoID'))})
                        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(plugin_handle)

def play(video_id, is_livestream='False', use_inputstream=False):
    log('Play video: ' + video_id)
    videoid = video_id
    partnerid = '2780'
    unassecret = 'aXHi21able'
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    ident = str(random.randint(10000000, 99999999)) + str(int(time.time()))
    streamtype = 'live' if is_livestream == 'True' else 'vod'
    auth = md5.new(videoid + partnerid + timestamp + unassecret).hexdigest()
    url = 'https://streamaccess.unas.tv/hdflash2/' + streamtype + '/' + partnerid + '/' + videoid + '.xml?format=iphone&streamid=' + videoid + '&partnerid=' + partnerid + '&ident=' + ident + '&timestamp=' + timestamp + '&auth=' + auth
    response = urllib.urlopen(url).read()
    xmlroot = ET.ElementTree(ET.fromstring(response))
    playlisturl = xmlroot.find('token').get('url')
    auth = xmlroot.find('token').get('auth')
    listitem = xbmcgui.ListItem(path=playlisturl + "?hdnea=" + auth)
    if use_inputstream is True:
        play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')    
    xbmcplugin.setResolvedUrl(plugin_handle, True, listitem)

def router(paramstring, use_inputstream=False):
    params = dict(parse_qsl(paramstring))
    keys = params.keys()
    log(params)
    if len(keys) == 0:
        show_sport_selection()
        return True
    if params.get('video_id', None) is not None:
        play(video_id=params.get('video_id'), is_livestream=params.get('is_livestream'), use_inputstream)
    if params.get('target', None) is not None:
        show_event_details(sport=params.get('for'), lane=params.get('lane'), target=params.get('target'))
        return True
    if params.get('lane', None) is not None:
        show_event_lane(sport=params.get('for'), lane=params.get('lane'))
        return True
    if params.get('for', None) is not None:
        show_sport_categories(sport=params.get('for'))
        return True


if __name__ == '__main__':
    # urllib ssl fix
    import ssl
    from functools import wraps
    def sslwrap(func):
        @wraps(func)
        def bar(*args, **kw):
            kw['ssl_version'] = ssl.PROTOCOL_TLSv1
            return func(*args, **kw)
        return bar
    ssl.wrap_socket = sslwrap(ssl.wrap_socket)    
    # Load addon data & start plugin
    addon = get_addon()
    addon_data = get_addon_data()
       log('Started (Version ' + addon_data.get('version') + ')')
    kodi_version = int(get_kodi_version())
    inputstream_version = int(get_inputstream_version().replace('.', ''))
    if inputstream_version < 999:
        inputstream_version = inputstream_version * 10
    log('Kodi Version: ' + str(kodi_version))
    log('Inputstream Version: ' + str(inputstream_version))
    # determine if we can use inputstream for HLS
    use_inputstream = False
    if kodi_version >= 17 and inputstream_version >= 2070:
        use_inputstream = True
    # setup in memory cache for epg data
    setup_memcache()
    # check if we have userdata settings
    #user = addon.getSetting('email')
    #password = addon.getSetting('password')
    # show user settings dialog if settings are not complete
    # store the credentials if user added them
    #if not has_credentials(user, password):
    #    user, password = set_credentials()
    # start request session to pass around
    #_session = get_session()
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    #router(sys.argv[2][1:], _session, user, password, use_inputstream)
    router(sys.argv[2][1:], use_inputstream)