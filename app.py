import logging, os
from telegram import Update, MessageOriginChannel, MessageOriginChat, MessageOriginUser, MessageOriginHiddenUser
from telegram.ext import *
from readwise import ReadWise
from datetime import datetime
import logging
from functools import wraps
from dotenv import load_dotenv
import utils
from markdown2 import Markdown
from requests.models import PreparedRequest
import requests
import re

load_dotenv()

# get bot token from env
BOT_TOKEN = os.getenv('BOT_TOKEN')
# initialize class for Readwise api
WISE = ReadWise(os.getenv('READWISE_TOKEN'))
# restrict access to our bot to avoid spam
ADMIN = os.getenv('ADMIN_USER_ID')

logging.FileHandler("info_telewise_bot.txt", mode='a', encoding=None, delay=False)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

FORWARD = range(1)

_logger = logging.getLogger()


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != int(ADMIN):
            print(f"Unauthorized access denied for {user_id}.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


def url_extracter(entities):
    for ent in entities:
        txt = entities[ent]
        if ent.type == ent.TEXT_LINK:
            # Text with embedded URL  
            return str(ent.url)
        elif ent.type == ent.URL:
            # Plain URL
            return str(txt)


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Bot for integration with ReadWise api and Telegram. Forward me posts and I will send them to your ReadWise. For more go to https://github.com/ixnet/telewise_bot")


@restricted
async def send_to_readwise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[+][+][+][+][+] Message from " + str(update.effective_user.id))

    # Check if message is forwarded
    if not update.message.forward_origin:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please forward a message from a channel/chat to use this feature."
        )
        return

    # Get chat info from forward_origin
    origin = update.message.forward_origin

    if isinstance(origin, MessageOriginChannel):
        # MessageOriginChannel
        chat_username = origin.chat.username
        message_id = origin.message_id
        telegram_link = f"<a href='https://t.me/{chat_username}/{message_id}'>Telegram Link</a>"
        from_who = chat_username
    elif isinstance(origin, MessageOriginChat):
        # MessageOriginChat (group)
        chat_title = origin.chat.title
        # No public link for groups, use a different approach
        telegram_link = "Telegram Link"
        from_who = chat_title
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="This feature only works with forwarded channel/group messages."
        )
        return

    # default note text
    note_txt = "from Telegram bot"

    # if the message contains only text, it will have text_html property, but if the message contains media the text of the message would be in the caption_html property
    text = update.message.text_html if update.message.caption_html is None else update.message.caption_html
    # applend telegram link to the post
    text = text + "\n\n" + telegram_link
    # getting only one link (first link in the post would be here) from the post itself.
    post_link = url_extracter(update.message.parse_entities())

    # check token for Readwise API before sending highlight
    WISE.check_token()
    # send post as Readwise highlight
    WISE.highlight(text=text,
                   title=from_who,
                   source_url=telegram_link,
                   highlight_url=post_link,
                   note=note_txt,
                   highlighted_at=str(datetime.now().isoformat())
                   )
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Message from %s was highlighted with note: %s" % (from_who, note_txt))


@restricted
async def prepare_reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sending data to Readwise Reader...")
    return FORWARD


@restricted
async def send_to_reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    WISE.check_token()

    # Check if message is forwarded and determine if it's a public channel
    origin = update.message.forward_origin
    is_forwarded = origin is not None

    is_public = False
    telegram_link = None

    if is_forwarded:
        if isinstance(origin, MessageOriginChannel):
            is_public = origin.chat.username is not None
            if is_public:
                telegram_link = f"https://t.me/{origin.chat.username}/{origin.message_id}"
        elif isinstance(origin, MessageOriginChat):
            is_public = origin.chat.username is not None
            if is_public:
                telegram_link = f"https://t.me/{origin.chat.username}/{origin.message_id}"

    tags = utils.get_tags(update.message)
    tags.extend(['텔레그램', 'telegram'])

    urls_to_save = []
    # if the message contains only text, it will have text_html property, but if the message contains media the text of the message would be in the caption_html property
    text = update.message.text if update.message.caption is None else update.message.caption
    # html = update.message.text_html if update.message.caption_html is None else update.message.caption_html

    urls = await utils.parse_urls(update.message)
    urls = await utils.filter_valid_urls(urls)
    if await utils.is_empty_text(text, urls, update.message.entities):
        text = ""
    else:
        if is_public and telegram_link:
            urls_to_save.append(telegram_link)
        else:
            md_text = update.message.text_markdown_v2_urled if update.message.caption_markdown_v2_urled is None else update.message.caption_markdown_v2_urled
            markdowner = Markdown()
            html_to_save = markdowner.convert(md_text)

            # Get message_id from forward_origin
            message_id = origin.message_id if origin else getattr(update.message, 'message_id', '')
            telegram_link = f'https://andromedarabbit.net/madeupurl/{message_id}'

            # Get author/title from origin
            author = None
            if origin:
                if isinstance(origin, MessageOriginChannel):
                    author = origin.chat.title
                elif isinstance(origin, MessageOriginChat):
                    author = origin.chat.title

            url_saved = WISE.save(
                url=telegram_link, tags=tags, title="텔레그램; " + text[:48],
                html=html_to_save, published_date=origin.date if origin else None,
                author=author,
            )

            if url_saved:
                _logger.warning('URL saved successfully: ' + url_saved)

    # summary = text[:128]

    # send post as Readwise highlight
    urls_to_save.extend(urls)

    for url in urls_to_save:
        if url.startswith('https://t.me'):
            url_to_bookmark = await telegram_url_to_save(url)
            if url_to_bookmark == url:
                md_text = update.message.text_markdown_v2_urled if update.message.caption_markdown_v2_urled is None else update.message.caption_markdown_v2_urled
                markdowner = Markdown()
                html_to_save = markdowner.convert(md_text)

                # Get author from origin
                author = None
                if origin and isinstance(origin, (MessageOriginChannel, MessageOriginChat)):
                    author = origin.chat.title

                url_saved = WISE.save(
                    url=url_to_bookmark, tags=tags, title="텔레그램; " + text[:48],
                    html=html_to_save, published_date=origin.date if origin else None,
                    author=author,
                )
            else:
                # Get author from origin
                author = None
                if origin and isinstance(origin, (MessageOriginChannel, MessageOriginChat)):
                    author = origin.chat.title

                url_saved = WISE.save(
                    url=url_to_bookmark, tags=tags, title="텔레그램; " + text[:48],
                    published_date=origin.date if origin else None,
                    author=author,
                )

            if url_saved:
                _logger.debug('URL saved successfully: ' + url_saved)

            continue

        WISE.save(url=url, tags=tags)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Working with Reader API...")
    return ConversationHandler.END


async def telegram_url_to_save(url: str) -> str:
    req = PreparedRequest()
    params = {'embed': "1", 'mode': "tme"}
    req.prepare_url(url, params)
    url_to_bookmark = req.url

    r = requests.get(
        url=url_to_bookmark
    )

    if r.status_code != 200 and r.status_code != 201:
        _logger.warning(r.text)
        return url

    if 'Please open Telegram to view this post' in r.text:
        return url

    return url_to_bookmark


@restricted
async def cancel(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops...")
    return ConversationHandler.END


if __name__ == '__main__':
    # start app
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    # register commands

    conv_handler_reader = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^a$"), prepare_reader)],
        states={
            FORWARD: [
                MessageHandler((filters.TEXT | filters.ATTACHMENT | filters.PHOTO) & ~filters.COMMAND,
                               send_to_readwise)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler_reader)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(
        MessageHandler((filters.TEXT | filters.ATTACHMENT | filters.PHOTO) & ~filters.COMMAND, send_to_reader))

    # run bot
    application.run_polling()
