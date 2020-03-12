from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from dotenv import load_dotenv
from lxml import html
import os
import requests
import sys
import logging
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KEYWORD, CHOOSING = range(2)

reply_keyboard = [['Yes', 'No']]
markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

load_dotenv()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
        updater.idle()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
        updater.idle()
else:
    logger.error("No MODE specified!")
    sys.exit(1)

def start(update, context):
    update.message.reply_text(
        'Hello beloved! What topic would you like search for today? '
        'Send /cancel to stop talking to me.\n\n')

    return KEYWORD

def keyword(update, context):

    response = requests.get(
    'https://www.bible.com/search/bible',
    params={'q': update.message.text,
            'category': 'bible',
            'version_id': '1588'},
    )

    logger.info("Request Status:", response.status_code)

    # to save results as a list
    all_verses= []

    # raw html from youversion
    tree = html.fromstring(response.content)
    all_verses.extend(tree.find_class('search-result')[0].iterchildren())
    a_verse = random.choice(all_verses).text_content()


    update.message.reply_text("{}\n\nWould you like to search for another topic?".format(a_verse),
                              reply_markup=markup)

    return CHOOSING

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Have a wonderful day. Daddy God loves you.')

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            KEYWORD: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, keyword)],
            CHOOSING: [MessageHandler(Filters.regex('^Yes$'), start),
                            MessageHandler(Filters.regex('^No$'), cancel)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    run(updater)

if __name__ == '__main__':
    main()
