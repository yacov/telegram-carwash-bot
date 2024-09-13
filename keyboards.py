from telegram import InlineKeyboardMarkup, InlineKeyboardButton

LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "he": "עברית"
}

def get_language_menu():
    keyboard = [[InlineKeyboardButton(name, callback_data=f"set_language|{code}") for code, name in LANGUAGES.items()]]
    return InlineKeyboardMarkup(keyboard)

async def get_main_keyboard(user_language):
    if user_language == "ru":
        language_text = "Язык"
        cars_today_text = "Машины сегодня"
    elif user_language == "he":
        language_text = "שפה"
        cars_today_text = "מכוניות היום"
    else:  # Default to English
        language_text = "Language"
        cars_today_text = "Cars Today"

    keyboard = [
        [InlineKeyboardButton(language_text, callback_data="language"),
         InlineKeyboardButton(cars_today_text, callback_data="cars_today")]
    ]
    return InlineKeyboardMarkup(keyboard)