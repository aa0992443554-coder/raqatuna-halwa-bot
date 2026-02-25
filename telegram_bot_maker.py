import telebot

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = 'YOUR_API_KEY'
bot = telebot.TeleBot(API_KEY)

# Creating a reply keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
button = telebot.types.KeyboardButton('Echo')
keyboard.add(button)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Welcome! Click the button below to echo your message:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text == 'Echo':
        bot.send_message(message.chat.id, 'Please send a message to echo:')
    else:
        bot.send_message(message.chat.id, message.text)

# Start the bot
bot.polling()