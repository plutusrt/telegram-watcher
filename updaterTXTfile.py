import json
import os
import hashlib
from telethon import TelegramClient, events, utils
import config
import translateAPI


FILE_HASHES = []

client = TelegramClient(config.TELEGRAM_SESSION_NAME, config.API_ID, config.API_HASH).start()
with open('groups.json', 'r') as openfile:
    groups = json.load(openfile)


def get_message_content_send(translated_message, channel_name, sender_name, is_file=False, file_size=None, file_hash=None):
    message = ""
    message += f"{channel_name} ({sender_name})\n"
    message += f"{translated_message}\n"
    if is_file:
        message += f"File: size {file_size:.2f} MB, hash {file_hash}\n"
    message += "-----------------------"
    return message

def get_file_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_size_mb(file_path):
    file_size = 0
    try:
        file_size = os.path.getsize(file_path)
        print(f"File Size in Bytes is {file_size}")
    except FileNotFoundError:
        print("File not found.")
    except OSError:
        print("OS error occurred.")
    return file_size / (1024 * 1024)

@client.on(events.NewMessage)
async def handler(event):
    is_file = False
    file_path = None
    file_size = 0
    file_hash = None

    sender = await event.get_sender()
    sender_name = utils.get_display_name(sender)
    chat_id = str(event.chat_id)
    if chat_id in groups:

        # Translate
        try:
            translation = event.text #translateAPI.translate_text(event.text, "en")
            source_language = "" #translation.detected_language_code
            translated_text = translation #translation.translated_text
        except Exception as e:
            print(f"[X] Error translating text. Error is: {e}")
            translated_text = ""

        # Download file
        if event.photo or event.file:
            is_file = True
            file_path = await event.download_media(file="files")
            file_size = get_file_size_mb(file_path)
            file_hash = get_file_md5(file_path)
        message_to_send = get_message_content_send(translated_message=translated_text, channel_name=groups[chat_id], sender_name=sender_name, is_file=is_file, file_size=file_size, file_hash=file_hash)

        # Send
        if is_file:
            print(f"[-] Sending message from {groups[chat_id]} ({sender_name}). With file hash: {file_hash}.")

            # Send only if it's new media
            if file_hash not in FILE_HASHES:
                FILE_HASHES.append(file_hash)
                await client.send_file(config.CHANNEL_ID, file_path, caption=message_to_send, link_preview=False)
            try:
                os.remove(file_path)
            except Exception as e:
                print("[X] Error removing file with path: {path}. Error is: {e}")

        else:
            print(f"[-] Sending message from {groups[chat_id]} ({sender_name}).")
            # First check we are allowed to send messages without files
            if not config.SHOULD_SEND_FILES_ONLY:
                await client.send_message(config.CHANNEL_ID, message_to_send, link_preview=False)
try:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
finally:
    client.disconnect()
