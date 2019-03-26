from datetime import datetime
from decouple import config
from pyrogram import Client, Filters
import pyrebase


api_id = config('API_ID', cast=int)
api_hash = config('API_HASH')
client_name = config('CLIENT_NAME')
app = Client(config('BOT_TOKEN'), api_id, api_hash)

firebase_config = {
    "apiKey": config('APIKEY'),
    "authDomain": config('AUTHDOMAIN'),
    "databaseURL": config('DATABASEURL'),
    "projectId": config('PROJECTID'),
    "storageBucket": config('STORAGEBUCKET'),
    "messagingSenderId": config('MESSAGINGSENDERID')
  }

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
storage = firebase.storage()


def handle_media(message):
    local_media = app.download_media(message)
    if message["video_note"]:
        file_name = "media/{}{}".format(message.date, message['video_note'].file_id)
        media_type = 'video_note'
    if message["voice"]:
        file_name = "media/{}{}".format(message.date, message['voice'].file_id)
        media_type = 'voice'
    if message["animation"]:
        file_name = "media/{}{}".format(message.date, message['animation'].file_id)
        media_type = 'animation'
    if message["photo"]:
        file_name = "media/{}{}".format(message.date, message['photo'].id)
        media_type = 'photo'
    if message["sticker"]:
        file_name = "media/{}{}".format(message.date, message.sticker.file_id)
        media_type = 'sticker'
    media = storage.child(file_name).put(local_media)
    return [media_type, storage.child(file_name).get_url(media['downloadTokens'])]


@app.on_message()
def my_handler(client, message):
    print(message)
    if message['reply_to_message']:
        if message.media:
            media = handle_media(message)
            db.child("moment/").update(
                {
                    "{}/media".format(message['reply_to_message']['message_id']): media[1],
                    "{}/type".format(message['reply_to_message']['message_id']): media[0]
                })

        else:
            db.child("moment/").update({"{}/content".format(message['reply_to_message']['message_id']): message["text"]})
        return
    if message['edit_date']:
        return db.child("moment/").update({"{}/content".format(message['message_id']): message["text"]})
    if message.media:
        media = handle_media(message)
        data = {"media": media[1], "created_at": str(datetime.now()), "type": media[0]}
        return db.child("moment/{}".format(message['message_id'])).set(data)
    data = {"content": message["text"], "created_at": str(datetime.now())}
    db.child("moment/{}".format(message['message_id'])).set(data)


app.run()
