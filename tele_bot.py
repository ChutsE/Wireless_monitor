import telebot 
import os
from get_pictures import take_picture

TOKEN = '6282709830:AAFNffMjdYvxetw28A1STjwZ8aL-RhUAy5I'
bot = telebot.TeleBot(TOKEN)

chat_id = 5790373219

_photo = 'picture.jpg'
_video = 'video.mp4'

@bot.message_handler(commands=["foto", "last_videos"])
def c_start(message):

    if message.text == '/foto':
        bot.reply_to(message, "aqui esta la foto vigilancia")
        take_picture()
        with open(_photo, 'rb')as photo_file:     
            bot.send_photo(message.chat.id, photo = photo_file)

    if message.text == '/last_videos':
        video_names = get_video_names()
        response = "Estos son los ultimos videos grabados:\n"
        for video_name in video_names[-10:]:
            response += " -" + video_name + "\n"
        bot.reply_to(message, response)
        

@bot.message_handler(content_types=["text"])
def bot_mensajes(message, videos_dir = "videos/"):
    video_names = get_video_names()
    if message.text in video_names:
        video_path = videos_dir + message.text
        with open(video_path, 'rb') as video_file:     
            bot.send_video(message.chat.id, video = video_file)
    else:
        bot.send_message(message.chat.id, "No he entendido, solo respondo a comandos definidos como:\n/foto  /last_videos\no al nombre del video que solicitas")

def polling():
    bot.infinity_polling()

def get_video_names(videos_dir = "/home/chuts/Documents/Wireless_monitor/videos/"):
    video_names = os.listdir(videos_dir)
    return sorted(video_names)
    


