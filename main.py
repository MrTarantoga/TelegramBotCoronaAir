from telegram.ext import Updater
from telegram import ParseMode
from Picture import GetPictureOfeCO2
from datetime import datetime, timedelta
import requests
from program_logic import Interaction
from queue import Queue
from DBConnection import DBConnection
from threading import Thread
from base64 import b64decode
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from time import sleep
from os import getenv

TOKEN = getenv("TOKEN")
DB_URL = getenv("DB_URL")

if TOKEN is None and DB_URL is None:
    print("TOKEN and DB_URL are not defined")
    exit(1)
elif TOKEN is None:
    print("TOKEN is not in environment defined")
    exit(1)
elif DB_URL is None:
    print("DB_URL is not defined")
    exit(1)

db = DBConnection(DB_URL)
current_chats = list()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

current_user = dict()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please send a qr-code to me!")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.MARKDOWN_V2,
                            text="""Hi, I'm the help text
*/quality*: Send the quality of the last 90 min \(argument: past time in minutes\).

Send me a picture with the room qr code to log in.

Write */logout* to remove a room.""")

def send_picture_eCO2(update, context):
    print("chat_id: {}".format(update.effective_chat.id))
    if update.effective_chat.id in current_user:
        picture_source = GetPictureOfeCO2(DB_URL)
        try:
            past_minutes = int(context.args[0])
        except:
            pictures = picture_source.getPicture(datetime.now() - timedelta(minutes=90), datetime.now(), current_user[update.effective_chat.id]["sensor_id"])
            caption = "Quality: {} - {}".format((datetime.now() - timedelta(minutes=90)).strftime("%m-%d-%YT%H:%M:%S"), datetime.now().strftime("%m-%d-%YT%H:%M:%S"))
        else:
            pictures = picture_source.getPicture((datetime.now() - timedelta(minutes=past_minutes)).strftime("%m-%d-%YT%H:%M:%S"), datetime.now().strftime("%m-%d-%YT%H:%M:%S"), current_user[update.effective_chat.id]["sensor_id"])
            caption = "Quality: {} - {}".format((datetime.now() - timedelta(minutes=past_minutes)).strftime("%m-%d-%YT%H:%M:%S"), datetime.now().strftime("%m-%d-%YT%H:%M:%S"))
        for picture in pictures:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=picture, caption=caption)
    else:
        while True:
            try:
                context.bot.send_message(chat_id=update.effective_chat.id, text="You are not logged in into room")
                break
            except:
                pass

def state_machine_Wrapper(bot, que: Queue, ir: Interaction):
    while True:
        message = que.get()
        if "log_in" in message.keys():
            while True:
                try:
                    # bot.send_message(ir.chat_id,message["log_in"])
                    break
                except:
                    pass
           # bot.send_message(chat_id=ir.chat_id, text="Are you still in the room?")
        elif "photo_message" in message.keys():
            print("Send picture")
            picture = BytesIO(b64decode(bytes(message["photo_message"][0])))
            while True:
                try:
                    bot.send_photo(chat_id=ir.chat_id, photo=picture, caption=message["photo_message"][1])
                    break
                except:
                    pass
        elif "finish" in message.keys():
            que.task_done()
            break
        elif "text_message" in message.keys():
            while True:
                try:
                    bot.send_message(ir.chat_id,message["text_message"])
                    break
                except:
                    pass
        que.task_done()

    

def qr_code_for_auth(update, context):
    que = Queue(-1)
    picture = context.bot.getFile(update.message.photo[-1].file_id)
    picture_media = requests.get(picture["file_path"])

    prl = Interaction(update.effective_chat.id,db,picture_media.content,que)
    if picture_media.content in current_user:
        current_user[picture_media.content]["queue"].put({"finish":None})

    current_user[update.effective_chat.id] = {
        "sensor_id": int(decode(Image.open(BytesIO(picture_media.content)))[-1].data.decode("ascii")),
        "program_logic": prl,
        "queue": que,
        "thread_handler": Thread(target=state_machine_Wrapper, args=[context.bot, que, prl],daemon=True),
        "start": datetime.now()
    }
    current_user[update.effective_chat.id]["thread_handler"].start()

def log_out(update, context):
    if update.effective_chat.id in current_user:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Log out successfull")
        current_user[update.effective_chat.id]["queue"].put({"finish":None})
        picture_source = GetPictureOfeCO2(DB_URL)
        try:
            picture = picture_source.getPicture(current_user[update.effective_chat.id]["start"], datetime.now(), current_user[update.effective_chat.id]["sensor_id"])[-1]
            timdelta_string = current_user[update.effective_chat.id]["start"].strftime("%m-%d-%YT%H:%M:%S") + " - " + datetime.now().strftime("%m-%d-%YT%H:%M:%S")
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=picture, caption="Final Report: {}".format(timdelta_string))
        except Exception as err:
            print(err)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, no data collected during log-in, not report created")
        current_user[update.effective_chat.id]["thread_handler"].join()
        del current_user[update.effective_chat.id]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="User not log in -> no log out possible")

def unknow_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm sorry, I'm not understanding your command")

from telegram.ext import MessageHandler, Filters

recv_qr_code = MessageHandler(Filters.photo, qr_code_for_auth)
dispatcher.add_handler(recv_qr_code)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

log_out_handler = CommandHandler('logOut', log_out)
dispatcher.add_handler(log_out_handler)

picture_eCO2_handler = CommandHandler('quality', send_picture_eCO2, pass_args=True)
dispatcher.add_handler(picture_eCO2_handler)

unknown_command_handler = MessageHandler(Filters.command, unknow_command)
dispatcher.add_handler(unknown_command_handler)

updater.start_polling()