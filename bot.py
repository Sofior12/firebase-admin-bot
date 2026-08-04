import telebot

TOKEN = "तुम्हारा_BotFather_का_पूरा_टोकन"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Firebase Admin Bot Online!")

print("Bot Started...")
bot.infinity_polling()
