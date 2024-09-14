import logging
from telegram import Update
import telegram
from telegram.ext import ContextTypes
from database import get_today_stats, get_yesterday_stats, get_worker_data
from keyboards import get_language_menu, get_main_keyboard, LANGUAGES
from message_constants import MESSAGES
from datetime import datetime
from utils import is_user_admin
from telegram.error import BadRequest

logger = logging.getLogger(__name__)

def get_message(key: str, language: str) -> str:
    return MESSAGES.get(language, MESSAGES["en"]).get(key, MESSAGES["en"][key])

def generate_message_text(stats, current_time, user_language):
    if user_language == "ru":
        message_text = f"<b>Статистика на {current_time}:</b>\n\n"
        message_text += f"🚿 <b>Помыто:</b> {stats['total_washed']}\n"
        message_text += f"   • Мойка: {stats['normal_wash']}\n"
        message_text += f"   • Клей: {stats['additional_cleaning']}\n"
        message_text += f"   • Легкая мойка: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Отполировано:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ деталей: {stats['full_polish']}\n"
        message_text += f"   • 1-3 детали: {stats['half_polish']}\n"
    elif user_language == "he":
        message_text = f"<b>סטטיסטיקה נכון ל-{current_time}:</b>\n\n"
        message_text += f"🚿 <b>נשטפו:</b> {stats['total_washed']}\n"
        message_text += f"   • שטיפה רגילה: {stats['normal_wash']}\n"
        message_text += f"   • ניקוי דבק: {stats['additional_cleaning']}\n"
        message_text += f"   • שטיפה קלה: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>הוברקו:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ חלקים: {stats['full_polish']}\n"
        message_text += f"   • 1-3 חלקים: {stats['half_polish']}\n"
    else:  # Default to English
        message_text = f"<b>Statistics as of {current_time}:</b>\n\n"
        message_text += f"🚿 <b>Washed:</b> {stats['total_washed']}\n"
        message_text += f"   • Regular wash: {stats['normal_wash']}\n"
        message_text += f"   • Glue cleaning: {stats['additional_cleaning']}\n"
        message_text += f"   • Light wash: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Polished:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ parts: {stats['full_polish']}\n"
        message_text += f"   • 1-3 parts: {stats['half_polish']}\n"
    return message_text

async def get_user_language(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    if 'user_languages' not in context.bot_data:
        context.bot_data['user_languages'] = {}
    return context.bot_data['user_languages'].get(user_id, "ru")  # Default to Russian

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_language = await get_user_language(context, user.id)
    message = get_message("welcome", user_language)
    username = user.username or ""  # Use an empty string if username is None
    await update.message.reply_text(message, reply_markup=get_main_keyboard(
        user_language, username
    ))

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = await get_user_language(context, update.effective_user.id)
    message = get_message("select_language", user_language)
    if update.message:
        await update.message.reply_text(message, reply_markup=get_language_menu())
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(message, reply_markup=get_language_menu())
        except BadRequest as e:
            if str(e) != "Message is not modified":
                raise  # Re-raise the exception if it's not the "not modified" error

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

    await query.edit_message_text(text=message, reply_markup=get_main_keyboard(
        lang_code, query.from_user.username or ""))

async def send_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        airtable_tables = context.bot_data.get('airtable_tables', {})
        if not all(table in airtable_tables for table in ['scans', 'cardryers', 'polish']):
            raise KeyError("One or more required Airtable tables not found")

        logger.info("Fetching today's stats from Airtable...")
        stats = await get_today_stats(airtable_tables)
        logger.info(f"Fetched stats: {stats}")

        current_time = datetime.now().strftime("%H:%M")

        user_id = update.effective_user.id if isinstance(update, Update) else update.from_user.id
        user_language = await get_user_language(context, user_id)
        message_text = generate_message_text(stats, current_time, user_language)

        if isinstance(update, Update):
            await update.message.reply_text(message_text, reply_markup=get_main_keyboard(
                user_language, update.effective_user.username or ""))
        else:
            await update.edit_message_text(message_text, reply_markup=get_main_keyboard(
                user_language, update.from_user.username or ""))

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
    elif query.data == "cars_yesterday":
        await send_yesterday_update(query, context)
    elif query.data == "language":
        await language_command(update, context)

async def send_yesterday_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        airtable_tables = context.bot_data.get('airtable_tables', {})
        if not all(table in airtable_tables for table in ['scans', 'cardryers', 'polish']):
            raise KeyError("One or more required Airtable tables not found")

        logger.info("Fetching yesterday's stats from Airtable...")
        stats = await get_yesterday_stats(airtable_tables)
        logger.info(f"Fetched yesterday's stats: {stats}")

        user_id = update.effective_user.id if isinstance(update, Update) else update.from_user.id
        user_language = await get_user_language(context, user_id)
        message_text = generate_yesterday_message_text(stats, user_language)

        if isinstance(update, Update):
            await update.message.reply_text(message_text, reply_markup=get_main_keyboard(
                user_language, update.effective_user.username or ""))
        else:
            await update.edit_message_text(message_text, reply_markup=get_main_keyboard(
                user_language, update.from_user.username or ""))

    except Exception as e:
        error_msg = f"Error in send_yesterday_update: {str(e)}"
        logger.exception(error_msg)
        user_id = update.effective_user.id if isinstance(update, Update) else update.from_user.id
        user_language = await get_user_language(context, user_id)
        if isinstance(update, Update):
            await update.message.reply_text(get_message("failed_update", user_language).format(str(e)))
        else:
            await update.answer(get_message("failed_update", user_language).format(str(e)), show_alert=True)

def generate_yesterday_message_text(stats, user_language):
    if user_language == "ru":
        message_text = "<b>Статистика за вчера:</b>\n\n"
        message_text += f"🚿 <b>Помыто:</b> {stats['total_washed']}\n"
        message_text += f"   • Обычная мойка: {stats['normal_wash']}\n"
        message_text += f"   • Очистка от клея: {stats['additional_cleaning']}\n"
        message_text += f"   • Легкая мойка: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Отполировано:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ деталей: {stats['full_polish']}\n"
        message_text += f"   • 1-3 детали: {stats['half_polish']}\n\n"
        message_text += f"💰 <b>Общая выручка:</b> {stats['revenue']} NIS"
    elif user_language == "he":
        message_text = "<b>סטטיסטיקה של אתמול:</b>\n\n"
        message_text += f"🚿 <b>נשטפו:</b> {stats['total_washed']}\n"
        message_text += f"   • שטיפה רגילה: {stats['normal_wash']}\n"
        message_text += f"   • ניקוי דבק: {stats['additional_cleaning']}\n"
        message_text += f"   • שטיפה קלה: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>הוברקו:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ חלקים: {stats['full_polish']}\n"
        message_text += f"   • 1-3 חלקים: {stats['half_polish']}\n\n"
        message_text += f"💰 <b>סך ההכנסות:</b> {stats['revenue']} NIS"
    else:  # Default to English
        message_text = "<b>Yesterday's statistics:</b>\n\n"
        message_text += f"🚿 <b>Washed:</b> {stats['total_washed']}\n"
        message_text += f"   • Regular wash: {stats['normal_wash']}\n"
        message_text += f"   • Glue cleaning: {stats['additional_cleaning']}\n"
        message_text += f"   • Light wash: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Polished:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ parts: {stats['full_polish']}\n"
        message_text += f"   • 1-3 parts: {stats['half_polish']}\n\n"
        message_text += f"💰 <b>Total revenue:</b> {stats['revenue']} NIS"
    return message_text
