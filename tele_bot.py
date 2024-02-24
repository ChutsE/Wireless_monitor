import telebot 
from get_pictures import take_picture

TOKEN = '6282709830:AAFNffMjdYvxetw28A1STjwZ8aL-RhUAy5I'
bot = telebot.TeleBot(TOKEN)

chat_id = 5790373219

_photo = 'picture.jpg'
_video = 'video.mp4'

@bot.message_handler(commands=["foto", "video"])
def c_start(message):

    if message.text == '/foto':
        bot.reply_to(message, "aqui esta la foto vigilancia")
        take_picture()
        with open(_photo, 'rb')as photo_file:     
            bot.send_photo(message.chat.id, photo = photo_file)

    if message.text == '/video':
        bot.reply_to(message, "aqui esta el video vigilancia")
        with open(_video, 'rb')as video_file:     
            bot.send_video(message.chat.id, video = video_file)

@bot.message_handler(content_types=["text"])
def bot_mensajes(message):
    bot.send_message(message.chat.id, "no he entendido, solo respondo a comandos definidos como  \n /audio  /foto  /video")

def polling():
    bot.infinity_polling()

