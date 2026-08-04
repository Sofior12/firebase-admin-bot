import telebot
import os
from dotenv import load_dotenv
from firebase import read_data

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🤖 Firebase Admin Bot\n\n"
        "/read - Read Firebase\n"
        "/devices - Show devices\n"
        "/messages - Show messages"
    )

@bot.message_handler(commands=['read'])
def read(message):
    data = read_data()
    bot.reply_to(message, str(data)[:4000])

@bot.message_handler(commands=['devices'])
def devices(message):
    data = read_data("devices")
    bot.reply_to(message, str(data)[:4000])

@bot.message_handler(commands=['messages'])
def messages(message):
    data = read_data("messages")
    bot.reply_to(message, str(data)[:4000])

print("Bot Started...")
bot.infinity_polling()
