from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils import is_user_admin
import logging
logger = logging.getLogger(__name__)

LANGUAGES = {
    "ru": "🇷🇺",
    "en": "🇬🇧",
    "he": "🇮🇱"
}

def get_language_menu():
    keyboard = [[InlineKeyboardButton(emoji, callback_data=f"set_language|{code}") for code, emoji in LANGUAGES.items()]]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard(user_language: str, username: str):
    language_text = "🌐"
    cars_today_text = {
        "ru": "🚗 Сегодня",
        "he": "🚗 היום",
        "en": "🚗 Today"
    }.get(user_language, "🚗 Today")

    cars_yesterday_text = {
        "ru": "🚙 Вчера",
        "he": "🚙 אתמול",
        "en": "🚙 Yesterday"
    }.get(user_language, "🚙 Yesterday")

    cars_month_text = {
        "ru": "🚕 Этот месяц",
        "he": "🚕 החודש",
        "en": "🚕 This Month"
    }.get(user_language, "🚕 This Month")

    keyboard = [
        [
            InlineKeyboardButton(language_text, callback_data="language"),
            InlineKeyboardButton(cars_today_text, callback_data="cars_today")
        ]
    ]

    if is_user_admin(username):
        keyboard[0].extend([
            InlineKeyboardButton(cars_yesterday_text, callback_data="cars_yesterday"),
            InlineKeyboardButton(cars_month_text, callback_data="cars_month")
        ])

    return InlineKeyboardMarkup(keyboard)
