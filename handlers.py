import logging
from telegram import Update
import telegram
from telegram.ext import ContextTypes
from database import get_today_stats, get_worker_data, update_worker_language
from keyboards import get_language_menu, get_main_keyboard, LANGUAGES
from message_constants import MESSAGES
from datetime import datetime

logger = logging.getLogger(__name__)

def get_message(key: str, language: str) -> str:
    return MESSAGES.get(language, MESSAGES["en"]).get(key, MESSAGES["en"][key])

def generate_message_text(stats, current_time, user_language):
    if user_language == "ru":
        message_text = f"1. Время: {current_time}. С начала дня сделано:\n"
        message_text += f"   * Помыто - {stats['total_washed']} (Мойка: {stats['normal_wash']}, Клей: {stats['additional_cleaning']}, Легкая мойка: {stats['light_wash']})\n"
        message_text += f"   * Отполировано - {stats['total_polished']} (4+ деталей: {stats['full_polish']}, 1-3 детали: {stats['half_polish']})"
    elif user_language == "he":
        message_text = f"1. זמן: {current_time}. מתחילת היום בוצעו:\n"
        message_text += f"   * נשטפו - {stats['total_washed']} (שטיפה: {stats['normal_wash']}, דבק: {stats['additional_cleaning']}, שטיפה קלה: {stats['light_wash']})\n"
        message_text += f"   * הוברקו - {stats['total_polished']} (4+ חלקים: {stats['full_polish']}, 1-3 חלקים: {stats['half_polish']})"
    else:  # Default to English
        message_text = f"1. Time: {current_time}. Since the beginning of the day:\n"
        message_text += f"   * Washed - {stats['total_washed']} (Wash: {stats['normal_wash']}, Glue: {stats['additional_cleaning']}, Light wash: {stats['light_wash']})\n"
        message_text += f"   * Polished - {stats['total_polished']} (4+ parts: {stats['full_polish']}, 1-3 parts: {stats['half_polish']})"
    return message_text

async def get_user_language(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    if 'user_languages' not in context.bot_data:
        context.bot_data['user_languages'] = {}
    return context.bot_data['user_languages'].get(user_id, "ru")  # Default to Russian

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_language = await get_user_language(context, user_id)
    message = get_message("welcome", user_language)
    await update.message.reply_text(message, reply_markup=await get_main_keyboard(user_language))

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = await get_user_language(context, update.effective_user.id)
    message = get_message("select_language", user_language)
    if update.message:
        await update.message.reply_text(message, reply_markup=get_language_menu())
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=get_language_menu())

async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang_code = query.data.split("|")[1]
    
    if 'user_languages' not in context.bot_data:
        context.bot_data['user_languages'] = {}
    context.bot_data['user_languages'][user_id] = lang_code
    
    language_name = LANGUAGES[lang_code]
    message = get_message("language_set", lang_code).format(language_name)
    
    await query.edit_message_text(text=message, reply_markup=await get_main_keyboard(lang_code))

async def send_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        airtable_tables = context.bot_data.get('airtable_tables', {})
        if 'scans' not in airtable_tables:
            raise KeyError("Scans table not found in Airtable tables")
        
        stats = await get_today_stats(airtable_tables['scans'])
        current_time = datetime.now().strftime("%H:%M")

        user_id = update.effective_user.id if isinstance(update, Update) else update.from_user.id
        user_language = await get_user_language(context, user_id)
        message_text = generate_message_text(stats, current_time, user_language)

        if isinstance(update, Update):
            await update.message.reply_text(message_text, reply_markup=await get_main_keyboard(user_language))
        else:
            try:
                await update.edit_message_text(message_text, reply_markup=await get_main_keyboard(user_language))
            except telegram.error.BadRequest as e:
                if str(e) == "Message is not modified":
                    await update.answer(get_message("stats_up_to_date", user_language))
                else:
                    raise

    except Exception as e:
        error_msg = f"Error in send_update: {str(e)}"
        logger.exception(error_msg)
        user_id = update.effective_user.id if isinstance(update, Update) else update.from_user.id
        user_language = await get_user_language(context, user_id)
        if isinstance(update, Update):
            await update.message.reply_text(get_message("failed_update", user_language).format(str(e)))
        else:
            await update.answer(get_message("failed_update", user_language).format(str(e)), show_alert=True)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cars_today":
        await send_update(query, context)
    elif query.data == "language":
        await language_command(update, context)