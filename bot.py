from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Firebase Admin Bot Online!")

print("Bot Started...")
bot.infinity_polling()
