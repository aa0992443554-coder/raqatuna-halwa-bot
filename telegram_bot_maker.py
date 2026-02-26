# Telegram Bot Maker

import logging
import sqlite3
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
from functools import wraps

# Setting up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
conn = sqlite3.connect('user_preferences.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS preferences (user_id INTEGER PRIMARY KEY, preference TEXT)''')

# Command validation decorator
def command_validation(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if not update.message:
            logger.warning('Message object not found')
            return
        return func(update, context, *args, **kwargs)
    return wrapper

# Rate limiting decorator
def rate_limit(limit):
    timestamps = {}  # Store user request timestamps

    def decorator(func):
        @wraps(func)
        def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
            user_id = update.message.from_user.id
            current_time = time.time()
            if user_id not in timestamps:
                timestamps[user_id] = []
            timestamps[user_id] = [timestamp for timestamp in timestamps[user_id] if current_time - timestamp < 1]
            if len(timestamps[user_id]) >= limit:
                logger.warning(f'Rate limit exceeded for user {user_id}')
                context.bot.send_message(chat_id=update.effective_chat.id, text='Rate limit exceeded. Please try again later.')
                return
            timestamps[user_id].append(current_time)
            return func(update, context, *args, **kwargs)
        return wrapper
    return decorator

# Command handlers
@command_validation
@rate_limit(5)
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f'User {user_id} started the bot.')
    update.message.reply_text('Hello! Welcome to the bot. Use /setpref to set your preferences.')

@command_validation
@rate_limit(5)
def set_pref(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    pref = context.args[0] if context.args else None
    if pref:
        cursor.execute('REPLACE INTO preferences (user_id, preference) VALUES (?, ?)', (user_id, pref))
        conn.commit()
        logger.info(f'User {user_id} set preference to {pref}.')
        update.message.reply_text(f'Preference set to: {pref}')
    else:
        update.message.reply_text('Please provide a preference.')

@command_validation
def get_pref(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    cursor.execute('SELECT preference FROM preferences WHERE user_id = ?', (user_id,))
    preference = cursor.fetchone()
    if preference:
        update.message.reply_text(f'Your preference is: {preference[0]}')
    else:
        update.message.reply_text('You have no preference set.')

def main():
    updater = Updater('YOUR_TOKEN', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('setpref', set_pref))
    dp.add_handler(CommandHandler('getpref', get_pref))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
