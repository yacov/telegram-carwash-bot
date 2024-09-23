import logging
import os
import datetime
from datetime import date, timedelta
from typing import Dict, Union, Tuple

import pytz
from dotenv import load_dotenv
from telegram import Chat, User, ChatMember, Bot
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from message_constants import MESSAGES

logger = logging.getLogger(__name__)

load_dotenv()

# Load admin usernames from environment variable
ADMIN_USERNAMES = [username.strip() for username in os.getenv('ADMIN_USERNAMES', '').split(',') if username.strip()]

async def is_user_admin(chat: Chat, user: User, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if chat.type == Chat.PRIVATE:
        return user.username in ADMIN_USERNAMES

    if not hasattr(context, 'chat_admins'):
        context.chat_admins = set()
        admins = await chat.get_administrators()
        context.chat_admins = {admin.user.id for admin in admins}

    return user.id in context.chat_admins

def calculate_revenue(scans_records):
    """
    Calculate the total revenue based on the car wash services performed.

    Parameters:
        scans_records (list): List of scan records containing service information.

    Returns:
        float: Total revenue in NIS.
    """
    # Prices for each service type
    prices = {
        'normal_wash': 70,
        'additional_cleaning': 145,
        'light_wash': 50
    }

    return sum(
        prices['additional_cleaning'] if scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning') else
        prices['light_wash'] if not scan['fields'].get('CleanGlue') and scan['fields'].get('ReturnCleaning') else
        prices['normal_wash']
        for scan in scans_records
    )

def get_message(key: str, language: str) -> str:
    return MESSAGES.get(language, MESSAGES["en"]).get(key, MESSAGES["en"][key])

def get_workdays_in_period(start_date: date, end_date: date) -> int:
    return sum(1 for day in range((end_date - start_date).days + 1) if (start_date + timedelta(day)).weekday() < 5)

async def get_chat_members(bot: Bot, chat_id: int) -> Dict[str, Union[Tuple[ChatMember, ...], int]]:
    """
    Fetch all admin members of a chat and the total member count.

    Args:
        bot (Bot): The bot instance.
        chat_id (int): The ID of the chat.

    Returns:
        Dict[str, Union[Tuple[ChatMember, ...], int]]: A dictionary containing:
            - 'administrators': A tuple of ChatMember objects representing the admin members.
            - 'member_count': The total number of members in the chat.
    """
    try:
        # Fetch all admin members
        administrators = await bot.get_chat_administrators(chat_id)

        # Get the total member count
        member_count = await bot.get_chat_member_count(chat_id)

        return {
            'administrators': administrators,
            'member_count': member_count
        }
    except TelegramError as e:
        logger.error(f"Error fetching chat members: {e}")
        return {
            'administrators': tuple(),
            'member_count': 0
        }

def get_israel_time():
    israel_tz = pytz.timezone('Asia/Jerusalem')
    return datetime.now(israel_tz)
