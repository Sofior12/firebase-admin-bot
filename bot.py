import telebot
import os

TOKEN = os.getenv("8851484835:AAECy2HKwSOgsiCysQDgy6IeDkw3W3ppxvo")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Firebase Admin Bot Online!")

print("Bot Started...")
bot.infinity_polling()
