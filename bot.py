import os
import random
import threading
import datetime
import json
from flask import Flask
import telebot
from telebot import types
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app for Render port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running! Send /start on Telegram"

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Initialize Firebase
FIREBASE_URL = os.getenv('FIREBASE_DATABASE_URL')
USE_SDK = False

try:
    # Try using Firebase Admin SDK
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_URL
    })
    USE_SDK = True
    print("✅ Firebase Admin SDK connected!")
except Exception as e:
    print(f"⚠️ Firebase SDK error: {e}")
    print("🔄 Using Firebase REST API...")
    USE_SDK = False

# Initialize bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Firebase Helper Functions
def firebase_get(path):
    """Get data from Firebase"""
    if USE_SDK:
        try:
            ref = db.reference(path)
            return ref.get()
        except Exception as e:
            print(f"SDK Get Error: {e}")
            return None
    else:
        try:
            url = f"{FIREBASE_URL}/{path}.json"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"REST Get Error: {e}")
            return None

def firebase_set(path, data):
    """Set data in Firebase"""
    if USE_SDK:
        try:
            ref = db.reference(path)
            ref.set(data)
            return True
        except Exception as e:
            print(f"SDK Set Error: {e}")
            return False
    else:
        try:
            url = f"{FIREBASE_URL}/{path}.json"
            response = requests.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"REST Set Error: {e}")
            return False

def firebase_update(path, data):
    """Update data in Firebase"""
    if USE_SDK:
        try:
            ref = db.reference(path)
            ref.update(data)
            return True
        except Exception as e:
            print(f"SDK Update Error: {e}")
            return False
    else:
        try:
            url = f"{FIREBASE_URL}/{path}.json"
            response = requests.patch(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"REST Update Error: {e}")
            return False

def firebase_delete(path):
    """Delete data from Firebase"""
    if USE_SDK:
        try:
            ref = db.reference(path)
            ref.delete()
            return True
        except Exception as e:
            print(f"SDK Delete Error: {e}")
            return False
    else:
        try:
            url = f"{FIREBASE_URL}/{path}.json"
            response = requests.delete(url)
            return response.status_code == 200
        except Exception as e:
            print(f"REST Delete Error: {e}")
            return False

# Generate random data
def generate_device_id():
    return ''.join(random.choices('0123456789ABCDEF', k=4))

def generate_number():
    return ''.join(random.choices('0123456789', k=10))

def generate_device_name():
    return ''.join(random.choices('0123456789abcdef', k=16))

# Main Menu Keyboard
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        "📱 Show Online Devices",
        "🔢 Generate Numbers",
        "📜 History",
        "🔍 Search Device ID",
        "👤 Profile",
        "🔄 Reset Bot",
        "📊 Stats",
        "❓ Help"
    ]
    for btn in buttons:
        keyboard.add(types.KeyboardButton(btn))
    return keyboard

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name
    
    # Save user to Firebase
    user_data = {
        'username': username,
        'user_id': user_id,
        'joined': datetime.datetime.now().isoformat(),
        'status': 'active',
        'last_active': datetime.datetime.now().isoformat()
    }
    firebase_update(f'users/{user_id}', user_data)
    
    welcome_text = f"""🎉 *Welcome to Soforotp Bot, {username}!*

I'm a powerful number generator and device manager with Firebase backend.

📌 *Features:*
• 📱 Generate random numbers with device IDs
• 👥 Track online devices in real-time
• 📜 View complete generation history
• 🔍 Search any device by ID
• 👤 Manage your profile
• 📊 View bot statistics

Use the buttons below to get started! 👇"""

    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_menu())

# Generate Numbers
@bot.message_handler(func=lambda message: message.text == "🔢 Generate Numbers")
@bot.message_handler(commands=['generate'])
def generate_numbers(message):
    processing_msg = bot.reply_to(message, "🔄 *Generating a random number...*", parse_mode='Markdown')
    
    # Generate data
    device_id = generate_device_id()
    number = generate_number()
    device_name = generate_device_name()
    db_num = random.randint(1, 99)
    timestamp = datetime.datetime.now().isoformat()
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name
    
    # Prepare device data
    device_data = {
        'device_id': device_id,
        'number': number,
        'device_name': device_name,
        'database': f'DB #{db_num}',
        'status': 'Online',
        'generated_at': timestamp,
        'generated_by': user_id,
        'generated_by_username': username,
        'last_active': timestamp
    }
    
    # Save to Firebase
    firebase_set(f'devices/{device_id}', device_data)
    
    # Save to history
    history_data = {
        'device_id': device_id,
        'number': number,
        'device_name': device_name,
        'generated_by': username,
        'generated_by_id': user_id,
        'timestamp': timestamp,
        'database': f'DB #{db_num}'
    }
    firebase_set(f'history/{timestamp}', history_data)
    
    # Update user stats
    user_stats = firebase_get(f'users/{user_id}/stats') or {'total_generated': 0}
    user_stats['total_generated'] = user_stats.get('total_generated', 0) + 1
    user_stats['last_generated'] = timestamp
    firebase_update(f'users/{user_id}', {'stats': user_stats})
    
    # Delete processing message
    bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
    
    # Create response with inline buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📤 Send Message", callback_data=f"send_{device_id}")
    btn2 = types.InlineKeyboardButton("📨 Receive OTP", callback_data=f"otp_{device_id}")
    btn3 = types.InlineKeyboardButton("📋 Copy Number", callback_data=f"copy_{number}")
    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    
    response = f"""✅ *Random Number Generated!*

🆔 *Device ID:* `{device_id}`
📱 *Number:* `{number}`
💻 *Device Name:* `{device_name}`
🗄️ *Database:* {db_num}
📊 *Status:* 🟢 Online
👤 *Generated By:* {username}
🕐 *Time:* {timestamp[:19]}

You can view this number in your History anytime."""

    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)

# Show Online Devices
@bot.message_handler(func=lambda message: message.text == "📱 Show Online Devices")
@bot.message_handler(commands=['devices'])
def show_devices(message):
    devices = firebase_get('devices')
    
    if not devices:
        bot.reply_to(
            message, 
            "❌ *No online devices found*\n\nUse /generate to create your first device!",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return
    
    # Filter online devices
    online_devices = {k: v for k, v in devices.items() if v.get('status') == 'Online'}
    
    if not online_devices:
        bot.reply_to(
            message,
            "❌ *No devices are currently online*\n\nGenerate a new device to see it here!",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return
    
    response = f"📱 *Online Devices* ({len(online_devices)})\n\n"
    response += "━━━━━━━━━━━━━━━━━━\n"
    
    for i, (device_id, data) in enumerate(list(online_devices.items())[:10], 1):
        response += f"*{i}.* 🆔 `{device_id}`\n"
        response += f"   📱 *Number:* `{data.get('number', 'N/A')}`\n"
        response += f"   💻 *Name:* `{data.get('device_name', 'N/A')}`\n"
        response += f"   🗄️ *DB:* {data.get('database', 'N/A')}\n"
        response += f"   👤 *By:* {data.get('generated_by_username', 'Unknown')}\n"
        response += f"   🕐 *Active:* {data.get('last_active', 'N/A')[:16]}\n"
        response += "━━━━━━━━━━━━━━━━━━\n"
    
    if len(online_devices) > 10:
        response += f"\n_...and {len(online_devices)-10} more devices_"
    
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_devices")
    btn2 = types.InlineKeyboardButton("📊 View All", callback_data="view_all_devices")
    keyboard.add(btn1, btn2)
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)

# History
@bot.message_handler(func=lambda message: message.text == "📜 History")
@bot.message_handler(commands=['history'])
def show_history(message):
    history = firebase_get('history')
    
    if not history:
        bot.reply_to(
            message,
            "❌ *No history found*\n\nGenerate some numbers first!",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return
    
    # Sort by timestamp (newest first)
    sorted_history = sorted(history.items(), key=lambda x: x[0], reverse=True)
    
    # Get user's history
    user_id = str(message.from_user.id)
    user_history = []
    
    for timestamp, data in sorted_history:
        if data.get('generated_by_id') == user_id:
            user_history.append((timestamp, data))
    
    if not user_history:
        bot.reply_to(
            message,
            "❌ *You haven't generated any numbers yet*\n\nUse /generate to create your first number!",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return
    
    response = f"📜 *Your Generation History* ({len(user_history)})\n\n"
    response += "━━━━━━━━━━━━━━━━━━\n"
    
    for i, (timestamp, data) in enumerate(user_history[:10], 1):
        response += f"*{i}.* 🆔 `{data.get('device_id', 'N/A')}`\n"
        response += f"   📱 *Number:* `{data.get('number', 'N/A')}`\n"
        response += f"   🗄️ *DB:* {data.get('database', 'N/A')}\n"
        response += f"   🕐 *Time:* {timestamp[:16]}\n"
        response += "━━━━━━━━━━━━━━━━━━\n"
    
    if len(user_history) > 10:
        response += f"\n_...and {len(user_history)-10} more entries_"
    
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_history")
    keyboard.add(btn)
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)

# Search Device ID
@bot.message_handler(func=lambda message: message.text == "🔍 Search Device ID")
def search_device_prompt(message):
    msg = bot.reply_to(
        message,
        "🔍 *Enter Device ID to search:*\n\nExample: `A938`\n\nYou can also send /search A938",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, search_device)

@bot.message_handler(commands=['search'])
def search_device_command(message):
    try:
        device_id = message.text.split(' ', 1)[1].strip().upper()
        perform_search(message, device_id)
    except:
        bot.reply_to(
            message,
            "❌ *Usage:* /search DEVICE_ID\n\nExample: /search A938",
            parse_mode='Markdown'
        )

def search_device(message):
    device_id = message.text.strip().upper()
    perform_search(message, device_id)

def perform_search(message, device_id):
    devices = firebase_get('devices')
    
    if not devices or device_id not in devices:
        bot.reply_to(
            message,
            f"❌ *Device `{device_id}` not found*\n\nTry searching for a valid device ID.",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        return
    
    data = devices[device_id]
    
    response = f"""✅ *Device Found!*

━━━━━━━━━━━━━━━━━━
🆔 *Device ID:* `{device_id}`
📱 *Number:* `{data.get('number', 'N/A')}`
💻 *Device Name:* `{data.get('device_name', 'N/A')}`
🗄️ *Database:* {data.get('database', 'N/A')}
📊 *Status:* {'🟢 Online' if data.get('status') == 'Online' else '🔴 Offline'}
👤 *Generated By:* {data.get('generated_by_username', 'Unknown')}
🕐 *Generated:* {data.get('generated_at', 'N/A')[:19]}
🕐 *Last Active:* {data.get('last_active', 'N/A')[:19]}
━━━━━━━━━━━━━━━━━━"""

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📤 Send Message", callback_data=f"send_{device_id}")
    btn2 = types.InlineKeyboardButton("📨 Get OTP", callback_data=f"otp_{device_id}")
    btn3 = types.InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_device_{device_id}")
    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)

# Profile
@bot.message_handler(func=lambda message: message.text == "👤 Profile")
@bot.message_handler(commands=['profile'])
def show_profile(message):
    user_id = str(message.from_user.id)
    user_data = firebase_get(f'users/{user_id}')
    
    if not user_data:
        bot.reply_to(
            message,
            "❌ *Profile not found*\n\nSend /start to create your profile!",
            parse_mode='Markdown'
        )
        return
    
    # Count user's generated numbers
    history = firebase_get('history')
    user_history = []
    if history:
        for timestamp, data in history.items():
            if data.get('generated_by_id') == user_id:
                user_history.append(data)
    
    # Get user's devices
    devices = firebase_get('devices')
    user_devices = []
    if devices:
        for device_id, data in devices.items():
            if data.get('generated_by') == user_id:
                user_devices.append(data)
    
    stats = user_data.get('stats', {})
    
    response = f"""👤 *Your Profile*

━━━━━━━━━━━━━━━━━━
📛 *Username:* {user_data.get('username', 'N/A')}
🆔 *User ID:* `{user_id}`
📅 *Joined:* {user_data.get('joined', 'N/A')[:19]}
📊 *Status:* {user_data.get('status', 'active').upper()}
🕐 *Last Active:* {user_data.get('last_active', 'N/A')[:19]}
━━━━━━━━━━━━━━━━━━
📊 *Statistics:*
• 🔢 Numbers Generated: {len(user_history)}
• 📱 Devices Created: {len(user_devices)}
• ⭐ Total Generations: {stats.get('total_generated', 0)}
━━━━━━━━━━━━━━━━━━"""

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_profile")
    btn2 = types.InlineKeyboardButton("📊 My Devices", callback_data="my_devices")
    keyboard.add(btn1, btn2)
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)

# Stats
@bot.message_handler(func=lambda message: message.text == "📊 Stats")
@bot.message_handler(commands=['stats'])
def show_stats(message):
    # Get all data
    devices = firebase_get('devices') or {}
    history = firebase_get('history') or {}
    users = firebase_get('users') or {}
    
    # Calculate stats
    total_devices = len(devices)
    online_devices = sum(1 for d in devices.values() if d.get('status') == 'Online')
    total_history = len(history)
    total_users = len(users)
    
    # Get recent activity
    recent_activity = []
    if history:
        sorted_history = sorted(history.items(), key=lambda x: x[0], reverse=True)
        for timestamp, data in sorted_history[:5]:
            recent_activity.append(f"• {data.get('generated_by', 'Unknown')} → `{data.get('number', 'N/A')}` ({timestamp[:16]})")
    
    response = f"""📊 *Bot Statistics*

━━━━━━━━━━━━━━━━━━
📱 *Devices:*
• Total: {total_devices}
• Online: {online_devices}
• Offline: {total_devices - online_devices}

👥 *Users:* {total_users}
🔢 *Total Generations:* {total_history}
━━━━━━━━━━━━━━━━━━

🕐 *Recent Activity:*
{chr(10).join(recent_activity) if recent_activity else 'No recent activity'}

━━━━━━━━━━━━━━━━━━
*Bot Status:* 🟢 Online
*Uptime:* Active
*Database:* Connected ✅"""

    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")
    keyboard.add(btn)
    
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=keyboard)

# Reset Bot
@bot.message_handler(func=lambda message: message.text == "🔄 Reset Bot")
def reset_bot(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✅ Yes, Reset Everything", callback_data="confirm_reset")
    btn2 = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_reset")
    keyboard.add(btn1, btn2)
    
    bot.reply_to(
        message,
        "⚠️ *⚠️ WARNING: Reset All Data ⚠️*\n\nThis will permanently delete:\n• All devices\n• All history\n• All user data\n\nAre you sure?",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

# Help
@bot.message_handler(func=lambda message: message.text == "❓ Help")
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """🤖 *Soforotp Bot Help*

📌 *Commands & Features:*

*Main Commands:*
• /start - Start the bot
• /generate - Generate random number
• /devices - Show online devices
• /history - View generation history
• /search DEVICE_ID - Search specific device
• /profile - View your profile
• /stats - View bot statistics
• /help - Show this help

*Buttons:*
• 📱 Show Online Devices - View all active devices
• 🔢 Generate Numbers - Create new random numbers
• 📜 History - See your generation history
• 🔍 Search Device ID - Find specific device
• 👤 Profile - View your user info
• 📊 Stats - View bot statistics
• 🔄 Reset Bot - Clear all data (Admin only)

*Admin Commands:*
• /users - List all users
• /delete PATH - Delete Firebase data
• /update PATH VALUE - Update Firebase data

🛠️ *Tips:*
• Data is stored in Firebase cloud
• All devices are tracked in real-time
• History shows your complete generation record

Need help? Contact @admin"""

    bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=main_menu())

# Admin Commands
@bot.message_handler(commands=['users'])
def list_users(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Unauthorized! Admin only.")
        return
    
    users = firebase_get('users')
    if not users:
        bot.reply_to(message, "❌ No users found")
        return
    
    response = "👥 *All Users*\n\n"
    response += "━━━━━━━━━━━━━━━━━━\n"
    for user_id, data in users.items():
        response += f"👤 {data.get('username', 'Unknown')}\n"
        response += f"🆔 `{user_id}`\n"
        response += f"📅 Joined: {data.get('joined', 'N/A')[:16]}\n"
        response += f"📊 Status: {data.get('status', 'unknown')}\n"
        response += "━━━━━━━━━━━━━━━━━━\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['update'])
def update_data(message):
    if not is_admin(message.from_user.id):
        return
    
    try:
    _, path, value = message.text.split() # Indented
    # Rest of your logic...
except Exception as e:
    print(f"Error: {e}") # Unindented, goes after the try block ends
    bot.reply_to(message, "Something went wrong.")
