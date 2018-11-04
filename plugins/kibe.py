import hashlib
import os
from amanobot.namedtuple import InlineKeyboardMarkup
from amanobot.exception import TelegramError
import config

bot = config.bot
bot_username = config.bot_username


def escape_markdown(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')

    return text


def kibe(msg):
    if msg.get('text'):
        if msg['text'].startswith('/kibe_stickerid') or msg['text'].startswith('!stickerid'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                bot.sendMessage(msg['chat']['id'], "Sticker ID:\n```" +
                                msg['reply_to_message']['sticker']['file_id'] + "```",
                                parse_mode='markdown')
            else:
                bot.sendMessage(msg['chat']['id'], "Please reply to a sticker to get its ID.")

        elif msg['text'].startswith('/kibe_getsticker') or msg['text'].startswith('!getsticker'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                chat_id = msg['chat']['id']
                file_id = msg['reply_to_message']['sticker']['file_id']
                bot.download_file(file_id, 'sticker.png')
                bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
                os.remove("sticker.png")
            else:
                bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to upload its PNG.")

        elif msg['text'].startswith('/kibe') or msg['text'].startswith('!kibe'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                user = msg['from']
                file_id = msg['reply_to_message']['sticker']['file_id']
                bot.download_file(file_id, str(msg['from']['id'])+'_kibe_sticker.png')
                hash = hashlib.sha1(bytearray(user['id'])).hexdigest()
                packname = "a" + hash[:20] + "_by_" + config.me['username']
                if len(msg['text'][5:]) > 0:
                    sticker_emoji = msg['text'].split()[1]
                else:
                    sticker_emoji = msg['reply_to_message']['sticker']['emoji']

                try:
                    bot.addStickerToSet(user_id=user['id'], name=packname,
                                        png_sticker=open(str(msg['from']['id'])+'_kibe_sticker.png', 'rb'), emojis=sticker_emoji)
                    os.remove(str(msg['from']['id'])+"_kibe_sticker.png")
                    bot.sendMessage(msg['chat']['id'],
                                    "Sticker successfully added to [pack](t.me/addstickers/%s)" % packname,
                                    parse_mode='markdown')
                except TelegramError as e:
                    if e.description == "Bad Request: STICKERSET_INVALID":
                        bot.sendMessage(msg['chat']['id'], "Use /make_kibe to create a pack first.")
                    print(e)
            else:
                bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to kibe it.")
        elif msg['text'].startswith('/make_kibe') or msg['text'].startswith('!make_kibe'):
            user = msg['from']
            name = user['first_name']
            name = name[:50]
            hash = hashlib.sha1(bytearray(user['id'])).hexdigest()
            packname = "a" + hash[:20] + "_by_" + config.me['username']
            try:
                success = bot.createNewStickerSet(user['id'], packname, name + "'s Kibe Amano Pack",
                                                  png_sticker="https://images.emojiterra.com/google/android-pie/512px/265f.png",
                                                  emojis='🦇')
            except TelegramError as e:
                print(e)
                if e.description == "Bad Request: sticker set name is already occupied":
                    bot.sendMessage(msg['chat']['id'],
                                    "Your pack can be found [here](t.me/addstickers/%s)" % packname,
                                    parse_mode='markdown')
                elif e.description == "Bad Request: PEER_ID_INVALID":
                    bot.sendMessage(msg['chat']['id'], "Contact me in PM first.",
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                        [dict(text='Start', url="t.me/{}".format(config.me['username']))]]))
                return

            if success:
                bot.sendMessage(msg['chat']['id'],
                                "Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname,
                                parse_mode='markdown')
            else:
                bot.sendMessage(msg['chat']['id'], "Failed to create sticker pack. Possibly due to blek mejik.")
