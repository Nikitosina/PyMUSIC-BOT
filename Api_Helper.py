import requests
from pprint import pprint


class LastFM:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.url = 'http://ws.audioscrobbler.com/2.0/'

    def get_top(self, artist=None, limit=10):
        params = {'api_key': self.key, 'method': 'artist.gettoptracks', 'format': 'json', 'limit': limit}
        if artist:
            params['artist'] = artist
        else:
            params['method'] = 'chart.gettoptracks'
        resp = requests.get(self.url, params=params).json()

        if artist:
            res = 'Итак, лучшие треки ' + resp['toptracks']['@attr']['artist'] + '\n\n'
            for track in resp['toptracks']['track']:
                res += track['@attr']['rank'] + '. ' + track['name'] + '\n'
        else:
            res = 'Итак, лучшие треки на данный момент:\n\n'
            for i in range(limit):
                track = resp['tracks']['track'][i]
                res += str(i + 1) + '. ' + track['artist']['name'] + ' - ' + track['name'] + '\n'
        return res[:-1]

    def get_info(self, artist, lang='ru'):
        params = {'api_key': self.key, 'method': 'artist.getinfo', 'format': 'json', 'lang': lang, 'artist': artist}
        resp = requests.get(self.url, params=params).json()

        res = 'Информация о ' + resp['artist']['name'] + '\n\n'

        res += 'Жанр: '
        for genre in resp['artist']['tags']['tag']:
            res += genre['name'] + ', '
        res += '\n\n'

        content = resp['artist']['bio']['content'].split('\n\n')
        if len('\n\n'.join(content[:1])) > 700:
            res += '\n\n'.join(content[:1])
        else:
            res += '\n\n'.join(content[:2])[:900] + '...'

        img_url = resp['artist']['image'][3]['#text']
        return res, img_url

    def get_track(self, track, artist=None):
        params = {'api_key': self.key, 'method': 'track.search', 'artist': artist, 'format': 'json', 'track': track}
        resp = requests.get(self.url, params=params).json()
        pprint(resp)
        data = resp['results']['trackmatches']['track'][0]

        res = data['artist'] + ' - ' + data['name']
        img_url = data['image'][-1]['#text']
        res += '\n\n' + data['url']
        return res, img_url


class YandexTranslator:
    def __init__(self, key, dest='en-ru'):
        self.url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
        self.key = key
        self.dest = dest

    def translate(self, text):
        response = requests.get(self.url,
            params={
                "key": self.key,
                "lang": self.dest,
                "text": text
            })
        return "\n\n".join([response.json()["text"][0]])
