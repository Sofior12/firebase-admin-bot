import telebot
import os
from dotenv import load_dotenv
from firebase import read_data
import random

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
    data = read_data()

    if not data:
        bot.reply_to(message, "No devices found")
        return

    # sirf keys jinke andar dict hai
    keys = [k for k, v in data.items() if isinstance(v, dict)]

    if not keys:
        bot.reply_to(message, "No devices found")
        return

    device = random.choice(keys)

    bot.reply_to(
        message,
        f"📱 Random Device\n\n"
        f"ID: {device}\n\n"
        f"{data[device]}"
    )
