import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request
from airtable import Airtable
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import PeerIdInvalid
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load .env file if it exists
load_dotenv()

# Telegram API credentials
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Airtable credentials
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('BASE_ID')

# Chat ID where the bot will send messages
CHAT_ID = os.environ.get('CHAT_ID')

# Initialize Airtable tables
scans_table = Airtable(BASE_ID, 'Scans', api_key=AIRTABLE_API_KEY)
cardryers_table = Airtable(BASE_ID, 'CarDryers', api_key=AIRTABLE_API_KEY)
polish_table = Airtable(BASE_ID, 'Polish', api_key=AIRTABLE_API_KEY)

# Initialize Pyrogram client
app = Client("WorkBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_today_stats():
    logger.info("Fetching today's stats")
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # Get scans (washes) for today
    scans = scans_table.get_all(formula=f"AND(IS_SAME({{Timestamp}}, '{today}', 'day'), IS_BEFORE({{Timestamp}}, '{tomorrow}'))")
    total_washed = len(scans)
    normal_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    additional_cleaning = sum(1 for scan in scans if scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    light_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and scan['fields'].get('ReturnCleaning'))
    dryed = cardryers_table.get_all(formula=f"AND(IS_SAME({{Work Started}}, '{today}', 'day'), IS_BEFORE({{Work Started}}, '{tomorrow}'))")
    total_dryed = len(dryed)

    # Get polishing jobs for today
    polished = polish_table.get_all(formula=f"AND(IS_SAME({{Timestamp}}, '{today}', 'day'), IS_BEFORE({{Timestamp}}, '{tomorrow}'))")
    total_polished = len(polished)
    full_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'FullPolish')
    half_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'HalfPolish')

    stats = {
        'total_processed': total_washed + total_dryed + total_polished,
        'total_washed': total_washed,
        'normal_wash': normal_wash,
        'additional_cleaning': additional_cleaning,
        'light_wash': light_wash,
        'total_dryed': total_dryed,
        'total_polished': total_polished,
        'full_polish': full_polish,
        'half_polish': half_polish
    }

    logger.info(f"Stats fetched: {stats}")
    return stats

def get_keyboard():
    """Generate the inline keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Cars Today", callback_data="cars_today")]
    ])

async def send_update(client, message):
    """Send update message."""
    logger.info("Sending update")
    try:
        stats = get_today_stats()
        current_time = datetime.now().strftime("%H:%M")

        message_text = f"1. Time: {current_time}. Cars processed today until now:\n"
        message_text += f"   * Total - {stats['total_processed']}\n"
        message_text += f"   * Washed - {stats['total_washed']} (Normal: {stats['normal_wash']}, Additional cleaning: {stats['additional_cleaning']}, Light wash: {stats['light_wash']})\n"
        message_text += f"   * Dried - {stats['total_dryed']}\n"
        message_text += f"   * Polished - {stats['total_polished']} (Full polish: {stats['full_polish']}, Half polish: {stats['half_polish']})"

        await message.reply(message_text, reply_markup=get_keyboard())
        logger.info("Message sent successfully")
    except Exception as e:
        error_msg = f"Error in send_update: {str(e)}"
        logger.exception(error_msg)
        await message.reply(f"Failed to send update. Error: {error_msg}")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    logger.info(f"Start command received from user {message.from_user.id}")
    await message.reply(
        "Hello! I'm your car wash bot (v2.0). Use the 'Cars Today' button below to get the latest stats.",
        reply_markup=get_keyboard()
    )

@app.on_callback_query()
async def handle_callback(client, callback_query):
    if callback_query.data == "cars_today":
        logger.info(f"Cars Today button pressed by user {callback_query.from_user.id}")
        await send_update(client, callback_query.message)
    await callback_query.answer()

@app.on_message(filters.command("getchatid"))
async def get_chat_id(client, message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id if message.message_thread_id else "Not a topic"
    logger.info(f"Chat ID {chat_id} and Thread ID {thread_id} requested by user {message.from_user.id}")
    await message.reply(f"The chat ID for this conversation is: {chat_id}\nThe topic ID (message_thread_id) is: {thread_id}")

@app.on_message(filters.command("cars"))
async def cars_command(client, message):
    await send_update(client, message)

# Flask app
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Hello. I am alive!"

# Function to run Flask asynchronously
async def run_flask():
    logger.info("Starting Flask server...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, flask_app.run, '0.0.0.0', int(os.environ.get('PORT', 8080)))

async def main():
    # Start Pyrogram client
    await app.start()
    logger.info("Pyrogram bot started.")

    # Run Flask server in parallel
    await run_flask()

    # Keep the bot running indefinitely
    await asyncio.Event().wait()

if __name__ == '__main__':
    logger.info("Starting the bot...")

    # Start the asyncio event loop
    asyncio.run(main())
