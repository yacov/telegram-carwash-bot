from telegram import InlineKeyboardMarkup, InlineKeyboardButton

LANGUAGES = {
    "ru": "🇷🇺",
    "en": "🇬🇧",
    "he": "🇮🇱"
}

def get_language_menu():
    keyboard = [[InlineKeyboardButton(emoji, callback_data=f"set_language|{code}") for code, emoji in LANGUAGES.items()]]
    return InlineKeyboardMarkup(keyboard)

async def get_main_keyboard(user_language):
    language_text = "🌐"  # Globe icon for language selection
    
    if user_language == "ru":
        cars_today_text = "🚗 Сегодня"
        cars_yesterday_text = "🚙 Вчера"
    elif user_language == "he":
        cars_today_text = "🚗 היום"
        cars_yesterday_text = "🚙 אתמול"
    else:  # Default to English
        cars_today_text = "🚗 Today"
        cars_yesterday_text = "🚙 Yesterday"
    
    keyboard = [
        [InlineKeyboardButton(language_text, callback_data="language"),
         InlineKeyboardButton(cars_today_text, callback_data="cars_today"),
         InlineKeyboardButton(cars_yesterday_text, callback_data="cars_yesterday")]
    ]
    return InlineKeyboardMarkup(keyboard)