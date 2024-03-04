import telebot 
import os
from get_pictures import take_picture

TOKEN = '6282709830:AAFNffMjdYvxetw28A1STjwZ8aL-RhUAy5I'
bot = telebot.TeleBot(TOKEN)

chat_id = 5790373219

_photo = 'picture.jpg'
_video = 'video.mp4'

@bot.message_handler(commands=["foto", "dates_record"])
def define_commands(message):

    if message.text == '/foto':
        bot.reply_to(message, "Aqui esta la foto vigilancia")
        take_picture()
        with open(_photo, 'rb')as photo_file:     
            bot.send_photo(message.chat.id, photo = photo_file)

    if message.text == '/dates_record':
        videos_dict = get_video_names()[0]
        dates = list(videos_dict.keys())
        response = "Estos son los dias que ha grabados:\n"
        for i in range(len(dates)):
            response += "  [" + str(i) + "] "+ dates[i] + "\n"
        bot.reply_to(message, response)

attempt = 0
date = ""
records = []
@bot.message_handler(content_types=["text"])
def bot_mensajes(message, videos_dir = "videos/"):
    global date, records, attempt
    videos_dict, videos_name = get_video_names()
    user_message = message.text

    if attempt == 0:
        dates = list(videos_dict.keys())
        try:
            date = dates[int(user_message)]
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "No he entendido, solo respondo a comandos definidos como:\n/foto  /dates_record \no ingresaste un indice incorrecto ")
        else:
            response = "Estos son los videos grabados del dia " + date +":\n"
            records = videos_dict[date]
            column = 0
            for i in range(len(records)):
                response += "  [" + str(i) + "]  " + records[i]
                if column == 1:
                    response += "\n"
                    column = 0
                else:
                    column += 1
            bot.reply_to(message, response)
            attempt = 1
    elif attempt == 1:
        try:
            time = records[int(user_message)]
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "ingresaste un indice incorrecto ")
        else:
            response = "Aqui el video del dia " + date +" a la hora " + time + "\n"
            bot.reply_to(message, response)
            index_matching = [i for i in range(len(videos_name)) if date and time in videos_name[i]] # regresa los indexes que contengan el date and hour 
            video_path = videos_dir + videos_name[index_matching[0]]
            with open(video_path, 'rb') as video_file:     
                bot.send_video(message.chat.id, video = video_file)
            date = ""
            records = []
            attempt = 0

def polling():
    bot.infinity_polling()

def get_video_names(videos_dir = "videos/"):
    video_names = sorted(os.listdir(videos_dir))
    videos_dict = videos_tree(video_names)
    return videos_dict, video_names

def videos_tree(video_names_list):
    videos_dict = {}
    date_prev = " "
    time_list = []
    len_videos = len(video_names_list)

    for i in range(len_videos):
        items = video_names_list[i].split(" ")
        date = items[3] + "/" + items[1] + "/" + items[5][:4]
        time = items[4]

        if (date != date_prev and i != 0) or (i == (len_videos - 1)):
            videos_dict[date_prev] = time_list
            time_list = []

        time_list.append(time)
        date_prev = date
    
    return videos_dict


