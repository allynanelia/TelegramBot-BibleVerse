from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from dotenv import load_dotenv
from lxml import html
import os
import requests
import re
import logging
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KEYWORD, CHOOSING = range(2)

reply_keyboard = [['Yes', 'No']]
markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


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
    update.message.reply_text('Bye! Have a wonderful day. Daddy God loves you.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    load_dotenv()

    updater = Updater(token=os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            KEYWORD: [MessageHandler(Filters.text, keyword)],
            # CONTINUE_SEARCH: [MessageHandler(Filters.regex('^(Yes|No)$'), continue_search)],
            CHOOSING: [MessageHandler(Filters.regex('^Yes$'), start),
                            MessageHandler(Filters.regex('^No$'), cancel)]

        },

        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^No$'), cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
