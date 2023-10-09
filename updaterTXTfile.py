import json
import os
import config
from telethon import TelegramClient, events, utils
import translateAPI

@client.on(events.NewMessage)
async def handler(event):
    sender = await event.get_sender()
    name = utils.get_display_name(sender)
    chat_id = event.chat_id
    if chat_id in groups:
        try:
            translation = translateAPI.translate_text(event.text, "en")
            source_language = translation.detected_language_code
            translated_text = translation.translated_text
        except:
            translated_text = ""
        if event.photo:
            path = await event.download_media(file="files")
            await client.send_file(config.CHANNEL_ID, path, caption=config.MONITOR_CHANNEL_ID[chat_id] + ": " + translated_text, link_preview=False)
            try:
                await os.remove(path)
            except Exception as e:
                print("photo: " +str(e))
        elif event.file:
            path = await event.download_media(file="files")
            try:
                await client.send_file(config.CHANNEL_ID, path, caption=config.MONITOR_CHANNEL_ID[chat_id] + ": " + translated_text, link_preview=False)
            except:
                pass
            try:
                await os.remove(path)
            except Exception as e:
                print("video: " + str(e))
        else:
            await client.send_message(config.CHANNEL_ID, config.MONITOR_CHANNEL_ID[chat_id] + ": " + translated_text , link_preview=False)
try:
    print('(Press Ctrl+C to stop this)')
    client = TelegramClient('test2', config.API_ID, config.API_HASH).start()
    with open('groups.json', 'r') as openfile:
        groups = json.load(openfile)
    client.run_until_disconnected()
finally:
    client.disconnect()
