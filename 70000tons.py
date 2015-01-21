#! /usr/bin/env python3

import json
import base64
import os

import requests
from bs4 import BeautifulSoup

class Band:
    def __init__(self, name, url, artist_id):
        self.name = name
        self.url = url
        self.artist_id = artist_id

bands = []

def load_templates(template_dir):
    templates = [template.split('.html')[0] for template in os.listdir(path=template_dir)]
    html = dict()
    for template in templates:
        with open(template_dir + '/' + template + '.html') as f:
            html[template] = f.read()
    return html

html = load_templates('templates')

with open('auth.json') as f:
    auth = json.load(f)

id_and_secret = auth['id'] + ':' + auth['secret']
id_and_secret = base64.b64encode(id_and_secret.encode()).decode()
spotify_auth_headers = {'Authorization': 'Basic ' + id_and_secret}
r = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'client_credentials'}, headers=spotify_auth_headers)
spotify_access_token = r.json()['access_token']
spotify_auth_headers = {'Authorization': 'Bearer ' + spotify_access_token}

r = requests.get('http://70000tons.com/artists/')

soup = BeautifulSoup(r.text)

soup = soup(class_='ib-block')

for i in soup:
    name = i.a.img['title']
    url = i.a['href'].split()[0]
    payload = {'q': name, 'type': 'artist'}
    r = requests.get('https://api.spotify.com/v1/search', params=payload, headers=spotify_auth_headers)
    if r.status_code == requests.codes.ok:
        try:
            artist_id = r.json()['artists']['items'][0]['id']
        except IndexError:
            artist_id = None
    else:
        artist_id = None
    bands.append(Band(name, url, artist_id))

out = ''
for band in bands:
    out += html['band'].format(name=band.name, url=band.url, artist_id=band.artist_id)

out = html['base'].format(content=out)

with open('70000tons.html', 'w') as f:
    f.write(out)

out = ''
for band in bands:
    out += band.name + '\n'

with open('70000tons.txt', 'w') as f:
    f.write(out)
