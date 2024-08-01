# -*- coding: utf-8 -*-
"""
    IPTV ORG Addon
    Copyright (C) 2024 Joel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from resources.modules.helper import *
import re

# IPTV ORG
# https://github.com/iptv-org/iptv

IPTV_ORG_README = 'https://github.com/iptv-org/iptv/raw/master/README.md'

def http(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    } 
    try:  
        r = requests.get(url,headers=headers)
        code = r.status_code
        if code == 200:
            src = r.content
            try:
                src = src.decode('utf-8')
            except:
                pass
            return src
        log('Error when accessing the url {0} with the code: {1}'.format(url,code))
    except Exception as e:
        log(e)
        return
    
def country_list():
    src = http(IPTV_ORG_README)
    if src:
        try:
            # split country list
            src = src.split('### Grouped by country')[1].split('###')[0]
            soup = BeautifulSoup(src, 'html.parser')
            rows = soup.find_all('tr')
            countries_links = []
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 3:
                    country = cells[0].get_text()
                    if not country.startswith("\u00A0") and not '&' in country and not '\\xc2' in country:
                        country_name = re.sub(r'^[\U0001F1E6-\U0001F1FF\s]+', '', country)
                        if 'International' in country_name:
                            try:
                                country_name = country_name[2:]
                            except:
                                pass
                        link = cells[2].get_text(strip=True)
                        countries_links.append((country_name, link))
            if countries_links:
                return countries_links
            log('iptv org countries not found')
            return
        except Exception as e:
            log(e)
            return


@route('/')
def index():
    setcontent('videos')
    addMenuItem({'name': '::: IPTV ORG :::', 'description': ''}, destiny='')
    addMenuItem({'name': 'List of countries', 'description': ''}, destiny='/iptv_country')
    end()
    setview('WideList')      


@route('/iptv_country')
def iptv_country(params):
    countries = country_list()
    if countries:
        setcontent('videos')
        addMenuItem({'name': '::: COUNTRIES :::', 'description': ''}, destiny='')
        for c in countries:
            country_name, url = c
            addMenuItem({'name': country_name.upper(), 'description': '', 'url': url}, destiny='/open_country')
        end()
        setview('WideList')
    else:
        log('Country list not found')    


@route('/open_country')
def open_country(params):
    country_name = params.get('name', '')
    url = params.get('url', '')
    if country_name and url:
        try:
            src = http(url)
            if src:
                m3u_match = re.search(r'#EXTM3U.*', src, re.DOTALL)
                if m3u_match:
                    m3u_content = m3u_match.group()
                else:
                    return
                pattern = r'#EXTINF:(.*?),(.*?)(?:\n(.*?))?(\n|$)'
                matches = re.findall(pattern, m3u_content, re.IGNORECASE)
                if matches:
                    setcontent('videos')
                    addMenuItem({'name': '::: {0} :::'.format(country_name), 'description': ''}, destiny='')
                    group_temp = []
                    for match in matches:
                        try:
                            groups_re, channel_name, channel_link, _ = match
                        except:
                            groups_re, channel_name, channel_link = match
                        try:
                            tvg_logo = re.findall(r'tvg-logo="(.*?)"', groups_re, re.IGNORECASE)[0]
                            tvg_logo = tvg_logo.strip()
                        except:
                            tvg_logo = ''
                        try:
                            group_title = re.findall(r'group-title="(.*?)"', groups_re, re.IGNORECASE)[0]
                            group_title = group_title.strip()
                            try:
                                group_title = group_title.decode('utf-8')
                            except:
                                pass
                        except:
                            group_title = ''
                        if group_title:
                            if not group_title in group_temp:
                                group_temp.append(group_title)
                                name = '[B]' + group_title + '[/B]'
                                item_data = {
                                            'name': name,
                                            'description': '',
                                            'group': group_title,
                                            'url': url
                                        }
                                try:                             
                                    addMenuItem(item_data, destiny='/open_group')
                                except:
                                    pass
                    end()
                    setview('WideList')
                else:
                    log('not data in open_country')
        except Exception as e:
            log(e)

@route('/open_group')
def open_group(params):
    url = params.get('url', '')
    group = params.get('group', '')
    if url and group:
        try:
            group = group.decode('utf-8')
        except:
            pass
        try:
            src = http(url)
            if src:
                m3u_match = re.search(r'#EXTM3U.*', src, re.DOTALL)
                if m3u_match:
                    m3u_content = m3u_match.group()
                else:
                    return
                pattern = r'#EXTINF:(.*?),(.*?)(?:\n(.*?))?(\n|$)'
                matches = re.findall(pattern, m3u_content, re.IGNORECASE)
                if matches:
                    setcontent('videos')                  
                    for match in matches:
                        try:
                            groups_re, channel_name, channel_link, _ = match
                        except:
                            groups_re, channel_name, channel_link = match
                        try:
                            channel_name = channel_name.decode('utf-8')                             
                        except:
                            pass
                        try:
                            tvg_logo = re.findall(r'tvg-logo="(.*?)"', groups_re, re.IGNORECASE)[0]
                            tvg_logo = tvg_logo.strip()
                        except:
                            tvg_logo = ''
                        if not tvg_logo:
                            tvg_logo = 'DefaultVideo.png'
                        try:
                            group_title = re.findall(r'group-title="(.*?)"', groups_re, re.IGNORECASE)[0]
                            group_title = group_title.strip()
                            try:
                                group_title = group_title.decode('utf-8')
                            except:
                                pass
                        except:
                            group_title = ''
                        if group_title:                          
                            if group_title == group:
                                name = '[B]' + channel_name + '[/B]'
                                item_data = {
                                            'name': name,
                                            'iconimage': tvg_logo,
                                            'description': '',
                                            'url': channel_link
                                        }
                                try:                               
                                    addMenuItem(item_data, destiny='/play_iptv', folder=False)
                                except:
                                    pass
                    end()
                    setview('WideList')
                else:
                    log('not data in open_group')
        except Exception as e:
            log(e) 

@route('/play_iptv')           
def play_iptv(params):
    play_video(params)          



