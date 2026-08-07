from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

markup = InlineKeyboardMarkup(row_width=2)

markup.add(
    InlineKeyboardButton("📱 Device Info", callback_data="device_info"),
    InlineKeyboardButton("🟢 Online", callback_data="online"),
)

markup.add(
    InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
    InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
)

bot.send_message(
    message.chat.id,
    f"""
🎲 <b>Random Device Found</b>

🆔 <b>Device ID:</b> {device_id}
📞 <b>Number:</b> {number}
📱 <b>Model:</b> {model}
🔋 <b>Battery:</b> {battery}%
🟢 <b>Status:</b> {status}
""",
    parse_mode="HTML",
    reply_markup=markup
)
