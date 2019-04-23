import telebot
import logging
from telebot import apihelper
from pprint import pprint
from Api_Helper import LastFM, YandexTranslator

logging.basicConfig(level=logging.INFO, filename='bot.log')

API_KEY = '423cad31da5633fa7e92daaea2c7170d'
API_SECRET = 'd741138b2ad7a61abbbcfb6b2926adab'

lfm = LastFM(API_KEY, API_SECRET)
yt = YandexTranslator('trnsl.1.1.20190407T111208Z.8aefe4bc9bb48f64.c75fe021dae573b3f89516244159eb075f0f0163')

bot = telebot.TeleBot('888587053:AAFXvpSr0VvvFkZZQOUlCveyzaeuImremQE')


@bot.message_handler(commands=['start'])
def handle_start(message):
    res = 'Привет! Я помогу тебе в мире музыки, вот что я умею:\n\n' \
          '/top <artist>, <limit> - лучшие треки <артиста>, <кол-во выводимых треков>\n' \
          '/info <artist> - информация об артисте'

    bot.send_message(message.from_user.id, res)


@bot.message_handler(commands=['top'])
def top(message):
    ans = 'Ничего не найдено, попробуйте еще раз'
    args = [i.strip() for i in ' '.join(message.text.split()[1:]).split(',')]
    print(args)
    if args[0].isdigit():
        ans = lfm.get_top(limit=int(args[0]))
    elif len(args) == 1:
        ans = lfm.get_top(args[0])
    elif len(args) == 2:
        ans = lfm.get_top(args[0], int(args[1]))
    bot.send_message(message.from_user.id, ans)


@bot.message_handler(commands=['info'])
def info(message):
    args = ' '.join([i.strip() for i in message.text.split()[1:]])
    ans, img_url = lfm.get_info(args)
    # ans = yt.translate(ans)
    print(len(ans))
    bot.send_photo(message.from_user.id, img_url, ans)


@bot.message_handler(commands=['track'])
def track(message):
    args = [i.strip() for i in ' '.join(message.text.split()[1:]).split(',')]
    if len(args) == 1:
        ans, img_url = lfm.get_track(args[0])
    else:
        ans, img_url = lfm.get_track(args[0], args[1])
    bot.send_photo(message.from_user.id, img_url, ans)


bot.polling(none_stop=True, interval=0)
