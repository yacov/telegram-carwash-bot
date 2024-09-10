import os
import logging
from datetime import datetime, timedelta

from airtable import Airtable
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid

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
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


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


async def send_update():
    logger.info("Sending update")
    try:
        stats = get_today_stats()
        current_time = datetime.now().strftime("%H:%M")

        message = f"1. Time: {current_time}. Cars processed today until now:\n"
        message += f"   * Total - {stats['total_processed']}\n"
        message += f"   * Washed - {stats['total_washed']} (Normal: {stats['normal_wash']}, Additional cleaning: {stats['additional_cleaning']}, Light wash: {stats['light_wash']})\n"
        message += f"   * Dried - {stats['total_dryed']}\n"
        message += f"   * Polished - {stats['total_polished']} (Full polish: {stats['full_polish']}, Half polish: {stats['half_polish']})"

        try:
            await app.send_message(CHAT_ID, message)
            logger.info(f"Message sent successfully to chat {CHAT_ID}")
            return True, "Update sent successfully!"
        except PeerIdInvalid:
            error_msg = f"Error: Invalid CHAT_ID {CHAT_ID}. Please check your .env file and ensure the bot has access to this chat."
            logger.error(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"Error in send_update: {str(e)}"
        logger.exception(error_msg)
        return False, error_msg


def schedule_updates():
    logger.info("Scheduling updates")
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_update, 'interval', minutes=10)
    scheduler.start()
    logger.info("Updates scheduled successfully")


@app.on_message(filters.command("start"))
async def start_command(client, message):
    logger.info(f"Start command received from user {message.from_user.id}")
    await message.reply(
        "Hello! I'm your car wash bot. I'll send updates every 30 minutes"
        " about the day's activities. Use /update to get the latest stats"
        " and /getchatid to get the current chat ID.")


@app.on_message(filters.command("update"))
async def manual_update(client, message):
    logger.info(f"Manual update requested by user {message.from_user.id}")
    success, result = await send_update()
    if success:
        logger.info("Manual update sent successfully")
        await message.reply(result)
    else:
        logger.error(f"Manual update failed: {result}")
        await message.reply(f"Failed to send update. Error: {result}")


@app.on_message(filters.command("getchatid"))
async def get_chat_id(client, message):
    chat_id = message.chat.id
    logger.info(f"Chat ID {chat_id} requested by user {message.from_user.id}")
    await message.reply(f"The chat ID for this conversation is: {chat_id}")


if __name__ == '__main__':
    logger.info("Starting the bot...")
    logger.info(f"Current CHAT_ID: {CHAT_ID}")
    schedule_updates()
    app.run()
