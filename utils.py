import os
from dotenv import load_dotenv
from message_constants import MESSAGES
from datetime import date, timedelta
from telegram import Chat, User, ChatMember
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Load admin usernames from environment variable
ADMIN_USERNAMES = [username.strip() for username in os.getenv('ADMIN_USERNAMES', '').split(',') if username.strip()]

async def is_user_admin(chat: Chat, user: User, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if chat.type == Chat.PRIVATE:
        return user.username in ADMIN_USERNAMES
    
    try:
        member = await chat.get_member(user.id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

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
