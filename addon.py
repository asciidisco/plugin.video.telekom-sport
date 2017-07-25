try:
   import cPickle as pickle
except:
   import pickle
import hashlib   
import urllib
import base64
import json
import time
import uuid
import re
import xml.etree.ElementTree as ET
from os import path, remove
from datetime import date, datetime
from urlparse import parse_qsl
import pyDes
import xbmcplugin
import xbmcgui
import xbmc
from xbmcaddon import Addon
from requests import session, utils
from bs4 import BeautifulSoup

# urls for login & data retrival
base_url = 'https://www.telekomsport.de'
login_link = base_url + '/service/auth/web/login?headto=https://www.telekomsport.de/info'
login_endpoint = 'https://accounts.login.idm.telekom.com/sso'
epg_url = base_url + '/api/v1/epg/1'
stream_definition_url = base_url + '/service/player/streamAccess?videoId=%VIDEO_ID%&label=2780_hls'

# setup plugin base stuff
plugin_handle = int(sys.argv[1])
kodi_base_url = sys.argv[0]

def get_session():
    addon_data = get_addon_data()
    return load_session(addon_data.get('cookie_path'))

def clear_session():
    addon_data = get_addon_data()
    file = addon_data.get('cookie_path')
    if path.isfile(file):
        remove(file)

def generateHash(text):
    return hashlib.sha224(text).hexdigest()

def uniq_id(t=1):
    mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if not ":" in mac_addr: mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    # hack response busy
    i = 0
    while not ":" in mac_addr and i < 3:
        i += 1
        time.sleep(t)
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
    if ":" in mac_addr and t == 1:
        device_id = str(uuid.UUID(md5(str(mac_addr.decode('utf-8'))).hexdigest()))
        addon.setSetting('device_id', device_id)
        return True
    elif ":" in mac_addr and t == 2:
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(mac_addr)).bytes
    else:
        log("[%s] error: failed to get device id (%s)" % (addon_id, str(mac_addr)))
        dialog.ok(addon_name, get_local_string(32008))
        return False

def encode(data):
    k = pyDes.triple_des(uniq_id(t=2), pyDes.CBC, "\0\0\0\0\0\0\0\0", padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    return base64.b64encode(d)

def decode(data):
    k = pyDes.triple_des(uniq_id(t=2), pyDes.CBC, "\0\0\0\0\0\0\0\0", padmode=pyDes.PAD_PKCS5)
    d = k.decrypt(base64.b64decode(data))
    return d

def save_session(_session, file):
    with open(file, 'w') as f:
        pickle.dump(utils.dict_from_cookiejar(_session.cookies), f)

def load_session(file):
    _session = session()
    if path.isfile(file): 
        with open(file, 'r') as f:
            _cookies = utils.cookiejar_from_dict(pickle.load(f))
            _session.cookies = _cookies
    return _session

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

def get_epg(_session):
    # check for cached epg data
    cached_epg = get_cached_item('epg')
    if cached_epg is not None:
        return cached_epg
    page_tree = {}
    epg = json.loads(_session.get(epg_url).text)
    if epg.get('status') == 'success':
        elements = epg.get('data').get('elements')
        for element in elements:
            element_date = date.fromtimestamp(float(element.get('date').get('utc_timestamp'))).strftime('%d.%m.%Y')
            if page_tree.get(element_date) is None:
                page_tree[element_date] = []
            slots = element.get('slots')
            for slot in slots:
                events = slot.get('events')
                for event in events:
                    page_tree.get(element_date).append({
                        'hash': generateHash(event.get('target_url')),
                        'url': base_url + event.get('target_url'),
                        'title': event.get('metadata').get('details').get('home').get('name_full') + ' - ' + event.get('metadata').get('details').get('away').get('name_full') + ' (' + datetime.fromtimestamp(float(event.get('metadata').get('scheduled_start').get('utc_timestamp'))).strftime('%H:%M') + ' Uhr)'
                    })
    add_cached_item('epg', page_tree)
    return page_tree

def get_player_ids(src):
    stream_id = re.search('stream-id=.*', src)
    if stream_id is None:
        return (None, None)
    return (re.search('stream-id=.*', src).group(0).split('"')[1], re.search('customer-id=.*', src).group(0).split('"')[1])

def get_stream_urls(_session, html_url):
    stream_urls = {}
    html_doc = _session.get(html_url).text
    soup = BeautifulSoup(html_doc, 'html.parser')
    media_types = soup.find('div', class_='mediatypes-wrapper')
    if media_types is None:
        stream_id, profile_id = get_player_ids(html_doc)
        stream_access = json.loads(_session.post(stream_definition_url.replace('%VIDEO_ID%', str(stream_id))).text)
        if stream_access.get('status') == 'success':
            stream_urls['Live'] = 'https:' + stream_access.get('data').get('stream-access')[1]
        return stream_urls
    media_type_sections = media_types.find_all('section')
    for media_type_section in media_type_sections:
        name = media_type_section.find_all('h4')[0].get_text()
        stream_id = media_type_section.find_all('a')[0].attrs.get('href').split('/')[-1:][0]
        stream_access = json.loads(_session.post(stream_definition_url.replace('%VIDEO_ID%', str(stream_id))).text)
        if stream_access.get('status') == 'success':
            stream_urls[name] = 'https:' + stream_access.get('data').get('stream-access')[1]
    return stream_urls

def get_m3u_url(_session, stream_url):
    m3u_url = ''
    root = ET.fromstring(_session.get(stream_url).text)
    for child in root:
        m3u_url = child.attrib.get('url') + '?hdnea=' + child.attrib.get('auth')
    return m3u_url

def get_addon():
    return Addon()

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

def show_date_list(_session):
    log('Main menu')
    addon_data = get_addon_data()
    epg = get_epg(_session)
    for date in epg.keys():
        title = ''
        items = epg.get(date)
        for item in items:
            title = title + str(' '.join(item.get('title').replace('Uhr', '').split(' ')[:-2]).encode('utf-8')) + '\n\n'
        url = build_url({'date': date})
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

def show_matches_list(_session, game_date):
    log('Games list')
    addon_data = get_addon_data()
    epg = get_epg(_session)
    date = epg.get(game_date)
    for item in date:
        url = build_url({'hash': item.get('hash'), 'date': game_date})
        li = xbmcgui.ListItem(label=item.get('title'))
        li.setProperty('fanart_image', addon_data.get('fanart'))        
        xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=True)
        xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(plugin_handle)

def show_match_details(_session, game_hash, game_date):
    log('Game details')
    addon_data = get_addon_data()    
    epg = get_epg(_session)
    date = epg.get(game_date)
    for item in date:
        if game_hash == item.get('hash'):
            streams = get_stream_urls(_session, item.get('url'))
            if len(streams.keys()) == 0:
                show_not_available_dialog()
                return
            for stream in streams:
                url = build_url({'hash': item.get('hash'), 'date': game_date, 'stream': stream})
                li = xbmcgui.ListItem(label=stream)
                li.setProperty('fanart_image', addon_data.get('fanart'))                  
                li.setProperty('IsPlayable', 'true')
                li.setInfo('video', {'title': stream, 'genre': 'Sports'})
                xbmcplugin.addDirectoryItem(handle=plugin_handle, url=url, listitem=li, isFolder=False)
                xbmcplugin.addSortMethod(handle=plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(plugin_handle)

def play(_session, name, game_hash, game_date):
    log('Play video: ' + str(name))
    epg = get_epg(_session)
    date = epg.get(game_date)
    for item in date:
        if game_hash == item.get('hash'):
            streams = get_stream_urls(_session, item.get('url'))
            for stream in streams:
                if stream == name:
                    log(streams.get(stream))
                    xbmcplugin.setResolvedUrl(plugin_handle, True, xbmcgui.ListItem(path=get_m3u_url(_session, streams.get(stream))))

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

def router(paramstring, _session, user, password):
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
            show_date_list(_session)
            return True
        if params.get('stream', None) is not None:
            play(_session, params.get('stream', None), params.get('hash', None), params.get('date', None))
            return True   
        if params.get('hash', None) is not None:
            show_match_details(_session, params.get('hash', None), params.get('date', None))
            return True    
        if params.get('date', None) is not None:
            show_matches_list(_session, params.get('date', None))
            return True
    else:
        show_login_failed_notification()

if __name__ == '__main__':
    # Load addon data & start plugin
    addon = get_addon()
    addon_data = get_addon_data()
    log('Started (Version ' + addon_data.get('version') + ')')
    # setup in memory cache for epg data
    setup_memcache()
    # check if we have userdata settings
    user = addon.getSetting('email')
    password = addon.getSetting('password')
    # show user settings dialog if settings are not complete
    # store the credentials if user added them
    if not has_credentials(user, password):
        user, password = set_credentials()
    # start request session to pass around
    _session = get_session()
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:], _session, user, password)
