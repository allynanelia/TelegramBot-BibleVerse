from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from dotenv import load_dotenv
from lxml import html
import os
import requests
import re
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KEYWORD = range(1)

def start(update, context):
    update.message.reply_text(
        'Hi! Please send me a keyword and I will return you a verse. '
        'Send /cancel to stop talking to me.\n\n')

    return KEYWORD

def keyword(update, context):
    response = requests.get(
    'https://www.bible.com/search/bible',
    params={'q': update.message.text,
            'category': 'bible',
            'version_id': '1588'},
    )
    # url = "https://www.bible.com/search/bible?q={0}&category=bible&version_id=1588".format(update.message.text)
    # contents = requests.get(url)
    logger.info("Request Status:", str(response.status_code))

    # raw html from youversion
    tree = html.fromstring(response.content)
    all_verses = tree.find_class('search-result')[0].iterchildren()

    # for a in all_verses:
    #     print('1', a.text_content())


    update.message.reply_text(next(all_verses).text_content())

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    load_dotenv()

    updater = Updater(token=os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher

    # start_handler = CommandHandler('start', start)
    # dp.add_handler(start_handler)
    # echo_handler = MessageHandler(Filters.text, echo)
    # dp.add_handler(echo_handler)

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            KEYWORD: [MessageHandler(Filters.text, keyword)]
            # ,BIBLEVERSE: [MessageHandler(Filters.text, bibleverse)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
