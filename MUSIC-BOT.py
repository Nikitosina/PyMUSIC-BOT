import telebot
import logging
import time
from Api_Helper import LastFM, YandexTranslator, MusiXmatch, readable_time

logging.basicConfig(level=logging.INFO, filename='bot.log')

API_KEY = '423cad31da5633fa7e92daaea2c7170d'
API_SECRET = 'd741138b2ad7a61abbbcfb6b2926adab'

lfm = LastFM(API_KEY, API_SECRET)
yt = YandexTranslator('trnsl.1.1.20190407T111208Z.8aefe4bc9bb48f64.c75fe021dae573b3f89516244159eb075f0f0163')
musix = MusiXmatch('348e28b8e5487d197cda48a17debe1bb')

print(musix.get_lyrics('seckn rkg'))
# print(musix.get_info_by_lyrics('Never say, nihilist of modern day'))

bot = telebot.TeleBot('888587053:AAFXvpSr0VvvFkZZQOUlCveyzaeuImremQE')


@bot.message_handler(commands=['start'])
def handle_start(message):
    res = 'Привет! Я помогу тебе в мире музыки, вот что я умею:\n\n' \
          '/top <*artist>, <*limit> - Лучшие треки <артиста>, <кол-во выводимых треков>\n' \
          '/info <artist> - Информация об артисте\n' \
          '/track <name>, <*artist> - Информация о треке\n' \
          '/album <artist>, <name> - Информация об альбоме\n' \
          '/lyrics <name>, <*artist> - Найти текст песни\n' \
          '/lyrics_search <text> - Найти песню по её тексту'

    bot.send_message(message.from_user.id, res)


@bot.message_handler(commands=['top'])
def top(message): # /top <Disturbed>, <5>
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
def info(message): # /info Disturbed
    args = ' '.join([i.strip() for i in message.text.split()[1:]])
    ans, img_url = lfm.get_info(args)
    # ans = yt.translate(ans)
    print(len(ans))
    bot.send_photo(message.from_user.id, img_url, ans)


@bot.message_handler(commands=['track'])
def track(message): # /track Stricken, <Disturbed>
    args = [i.strip() for i in ' '.join(message.text.split()[1:]).split(',')]
    if len(args) == 1:
        ans, img_url = lfm.get_track(args[0])
    else:
        ans, img_url = lfm.get_track(args[0], args[1])
    bot.send_photo(message.from_user.id, img_url, ans)


@bot.message_handler(commands=['album'])
def album(message): # /album Disturbed, Ten Thousand Fists
    args = [i.strip() for i in ' '.join(message.text.split()[1:]).split(',')]
    ans, img_url = lfm.get_album(args[0], args[1])
    bot.send_photo(message.from_user.id, img_url, ans)


@bot.message_handler(commands=['lyrics'])
def lyrics(message): # /lyrics Stricken, <Disturbed>
    args = [i.strip() for i in ' '.join(message.text.split()[1:]).split(',')]
    if len(args) == 1:
        ans = musix.get_lyrics(args[0])
    else:
        ans = musix.get_lyrics(args[0], args[1])
    bot.send_message(message.from_user.id, ans)


@bot.message_handler(commands=['lyrics_search'])
def lyrics_search(message): # /lyrics_search <text>
    args = ' '.join([i.strip() for i in message.text.split()[1:]])
    ans = musix.get_info_by_lyrics(args)
    bot.send_message(message.from_user.id, ans)


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        time.sleep(5)
