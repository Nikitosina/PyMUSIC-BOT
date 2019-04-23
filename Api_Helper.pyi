import requests

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