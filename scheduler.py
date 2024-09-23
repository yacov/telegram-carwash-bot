import logging
from datetime import time

import pytz
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import get_today_stats
from handlers import generate_message_text
from keyboards import get_main_keyboard
from utils import get_chat_members, get_israel_time

logger = logging.getLogger(__name__)

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    airtable_tables = context.bot_data.get('airtable_tables', {})

    if 'scans' not in airtable_tables:
        logger.error("Scans table not found in Airtable tables")
        return

    stats = await get_today_stats(airtable_tables)
    current_time = get_israel_time().strftime("%H:%M")

    # Get chat members info
    chat_members_info = await get_chat_members(context.bot, chat_id)
    administrators = chat_members_info['administrators']

    # Get the Chat object once
    chat = await context.bot.get_chat(chat_id)

    # Cache admin IDs in context
    context.chat_admins = {admin.user.id for admin in administrators}

    for admin in administrators:
        user_id = admin.user.id
        user_language = context.bot_data.get('user_languages', {}).get(user_id, 'ru')

        message_text = generate_message_text(stats, current_time, user_language)
        keyboard = await get_main_keyboard(user_language, chat, admin.user, context)

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send message to admin {user_id}: {str(e)}")

    logger.info(f"Daily report sent to {len(administrators)} admins in chat {chat_id}")

def schedule_daily_report(application, chat_id):
    israel_time = pytz.timezone('Asia/Jerusalem')
    application.job_queue.run_daily(
        send_daily_report,
        time(hour=23, minute=59, tzinfo=israel_time),
        chat_id=chat_id,
        data={'language': 'ru'}
    )
