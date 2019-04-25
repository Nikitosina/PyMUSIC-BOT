import requests
from pprint import pprint


class LastFM:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.url = 'http://ws.audioscrobbler.com/2.0/'

    def abort_case(self, resp):
        if 'error' in resp:
            return True
        return False

    def get_top(self, artist=None, limit=10):
        params = {'api_key': self.key, 'method': 'artist.gettoptracks', 'format': 'json', 'limit': limit}
        if artist:
            params['artist'] = artist
        else:
            params['method'] = 'chart.gettoptracks'
        resp = requests.get(self.url, params=params).json()
        if self.abort_case(resp):
            return 'Что-то пошло не так, попробуйте ещё раз'

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
        if self.abort_case(resp):
            return 'Что-то пошло не так, попробуйте ещё раз'

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
        if self.abort_case(resp):
            return 'Что-то пошло не так, попробуйте ещё раз'
        data = resp['results']['trackmatches']['track'][0]

        res = data['artist'] + ' - ' + data['name']
        img_url = data['image'][-1]['#text']
        res += '\n\n' + data['url']
        return res, img_url

    def get_album(self, artist, album):
        params = {'api_key': self.key, 'method': 'album.getinfo', 'artist': artist, 'album': album, 'format': 'json'}
        resp = requests.get(self.url, params=params).json()
        if self.abort_case(resp):
            return 'Что-то пошло не так, попробуйте ещё раз'

        res = resp['album']['artist'] + ' - ' + resp['album']['name'] + '\n'
        duration = 0
        tracks = ''
        for track in resp['album']['tracks']['track']:
            duration += int(track['duration'])
            tracks += track['@attr']['rank'] + '. ' + track['name'] + ' (' + readable_time(
                int(track['duration'])) + ')\n'
        res += 'Продолжительность: ' + readable_time(duration) + '\n\n'
        res += tracks[:-1] + '\n\n'
        res += resp['album']['url']
        img_url = resp['album']['image'][-1]['#text']
        return res, img_url


class MusiXmatch:
    def __init__(self, key):
        self.key = key
        self.url = 'https://api.musixmatch.com/ws/1.1/'

    def abort_case(self, resp):
        if resp['message']['header']['status_code'] != 200:
            return True
        return False

    def get_track_info(self, track=None, artist=None):
        url = self.url + 'track.search'
        params = {'apikey': self.key, 'q_artist': artist, 'q_track': track, 's_track_rating': 'desc'}
        resp = requests.get(url, params=params).json()
        if self.abort_case(resp) or not resp['message']['body']['track_list']:
            return 'укыс', 'acre', 'awfce', 'awefer', 'afcers'

        for track in resp['message']['body']['track_list']:
            if track['track']['has_lyrics'] == 1:
                return track['track']['track_name'], track['track']['album_name'], track['track']['artist_name'], \
                       track['track']['track_id'], track['track']['track_share_url']

    def get_lyrics(self, track, artist=None):
        name, album, art, track_id, full_lyrics = self.get_track_info(track, artist)
        url = self.url + 'track.lyrics.get'
        params = {'apikey': self.key, 'track_id': track_id}
        resp = requests.get(url, params=params).json()
        if self.abort_case(resp) or not resp['message']['body']:
            return 'Что-то пошло не так, попробуйте ещё раз'

        res = art + ' - ' + name + '\n\n'
        lyrics = resp['message']['body']['lyrics']['lyrics_body']
        lyrics = lyrics[:lyrics.rfind('...') + 3]
        res += lyrics + '\n\n' + 'Полный текст: ' + full_lyrics
        return res

    def get_info_by_lyrics(self, lyrics, limit=10):
        url = self.url + 'track.search'
        params = {'apikey': self.key, 'q_lyrics': lyrics, 'page_size': limit, 's_track_rating': 'desc'}
        resp = requests.get(url, params=params).json()
        if self.abort_case(resp):
            return 'Что-то пошло не так, попробуйте ещё раз'
        track_list = resp['message']['body']['track_list']

        res = 'Совпадения:\n\n'
        for i in range(len(track_list)):
            track = track_list[i]['track']
            res += str(i + 1) + '. ' + track['artist_name'] + ' - ' + track['track_name']
            if track['primary_genres']['music_genre_list']:
                res += ' (' + track['primary_genres']['music_genre_list'][0]['music_genre']['music_genre_name'] + ')'
            res += '\n'

        return res[:-1]

    def get_related(self, artist, limit=10):
        # https://api.musixmatch.com/ws/1.1/artist.related.get?artist_id=142&page_size=5&page=1&apikey=348e28b8e5487d197cda48a17debe1bb
        url = self.url + 'artist.search'
        params = {'apikey': self.key, 'q_artist': artist, 'page_size': 1}
        resp = requests.get(url, params=params).json()

        if self.abort_case(resp) or not resp['message']['body']['artist_list']:
            return 'Что-то пошло не так, попробуйте ещё раз'
        id = resp['message']['body']['artist_list'][0]['artist']['artist_id']

        url = self.url + 'artist.related.get'
        params = {'apikey': self.key, 'artist_id': id, 'page_size': limit, 'page': 1}
        resp = requests.get(url, params=params).json()

        if self.abort_case(resp) or not resp['message']['body']['artist_list']:
            return 'Что-то пошло не так, попробуйте ещё раз'

        res = f'Артисты, похожие на {artist.title()}:\n\n'
        for i in range(len(resp['message']['body']['artist_list'])):
            artist = resp['message']['body']['artist_list'][i]
            res += str(i + 1) + '. ' + artist['artist']['artist_name'] + '\n'
        return res[:-1]


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


def readable_time(secs):
    minutes = secs // 60
    secs = secs % 60
    res = str(minutes) + ':' + str(secs)
    return res
