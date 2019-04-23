import telebot
import pylast
import json
import requests
from pprint import pprint


def get_top(artist=None, limit=10):
    params = {'api_key': API_KEY, 'method': 'artist.gettoptracks', 'format': 'json', 'limit': limit}
    if artist:
        params['artist'] = artist
    else:
        params['method'] = 'chart.gettoptracks'
    resp = requests.get(lfm_url, params=params).json()

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


lfm_url = 'http://ws.audioscrobbler.com/2.0/'
API_KEY = '423cad31da5633fa7e92daaea2c7170d'
API_SECRET = 'd741138b2ad7a61abbbcfb6b2926adab'
username = 'Nikit0s90'
password = pylast.md5('Nikitos-123')

bot = telebot.TeleBot('888587053:AAFXvpSr0VvvFkZZQOUlCveyzaeuImremQE')


@bot.message_handler(commands=['start'])
def handle_start(message):
    res = 'Привет! Я помогу тебе в мире музыки, вот что я умею:\n\n' \
          '/top <artist>, <limit> - лучшие треки <артиста>'

    bot.send_message(message.from_user.id, res)


@bot.message_handler(commands=['top'])
def top(message):
    ans = 'Ничего не найдено, попробуйте еще раз'
    args = [i.strip() for i in ' '.join(message.text.split()[1:]).split(',')]
    print(args)
    if args[0].isdigit():
        ans = get_top(limit=int(args[0]))
    elif len(args) == 1:
        ans = get_top(args[0])
    elif len(args) == 2:
        ans = get_top(args[0], int(args[1]))
    bot.send_message(message.from_user.id, ans)


bot.polling(none_stop=True, interval=0)
