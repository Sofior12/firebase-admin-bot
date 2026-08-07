from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

markup = InlineKeyboardMarkup(row_width=2)

markup.add(
    InlineKeyboardButton("📱 Device Info", callback_data="device_info"),
    InlineKeyboardButton("🟢 Online", callback_data="online")
)

markup.add(
    InlineKeyboardButton("🔋 Battery", callback_data="battery"),
    InlineKeyboardButton("🔄 Refresh", callback_data="refresh")
)

text = f"""
🎲 <b>Random Device Found!</b>

🆔 <b>Device ID:</b> {device_id}
📞 <b>Number:</b> {number}
📱 <b>Device Name:</b> {model}
🟢 <b>Status:</b> {status}

💡 <i>Select an action below.</i>
"""

bot.send_message(
    message.chat.id,
    text,
    parse_mode="HTML",
    reply_markup=markup
)
