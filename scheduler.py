from telegram.ext import ContextTypes
from database import get_today_stats
from handlers import generate_message_text
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    language = context.job.data.get('language', 'en')
    airtable_tables = context.bot_data.get('airtable_tables', {})
    
    if 'scans' not in airtable_tables:
        logger.error("Scans table not found in Airtable tables")
        return

    stats = await get_today_stats(airtable_tables)
    current_time = datetime.now().strftime("%H:%M")
    message_text = generate_message_text(stats, current_time, language)
    await context.bot.send_message(chat_id=chat_id, text=message_text)

def schedule_daily_report(application, chat_id):
    application.job_queue.run_daily(send_daily_report, time(hour=23, minute=59), chat_id=chat_id, data={'language': 'ru'})
