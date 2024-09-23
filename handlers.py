import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import get_today_stats, get_yesterday_stats, get_monthly_stats
from keyboards import get_language_menu, get_main_keyboard, LANGUAGES
from utils import get_israel_time
from utils import is_user_admin, get_message

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_language = context.user_data.get('language', 'ru')
    message = get_message("welcome", user_language)
    keyboard = await get_main_keyboard(user_language, chat, user, context)
    await update.message.reply_text(message, reply_markup=keyboard)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'ru')
    message = get_message("select_language", user_language)
    chat = update.effective_chat
    user = update.effective_user
    keyboard = await get_main_keyboard(user_language, chat, user, context)
    if update.message:
        await update.message.reply_text(message, reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text=message, reply_markup=keyboard)

async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language = query.data.split("|")[1]

    # Save the selected language in user_data
    context.user_data['language'] = language

    # Also save it in bot_data for persistence across restarts
    if 'user_languages' not in context.bot_data:
        context.bot_data['user_languages'] = {}
    context.bot_data['user_languages'][update.effective_user.id] = language

    message = get_message("language_set", language).format(LANGUAGES[language])
    chat = update.effective_chat
    user = update.effective_user
    keyboard = await get_main_keyboard(language, chat, user, context)
    await query.edit_message_text(
        text=message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def send_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        user_language = context.user_data.get('language', 'ru')
        airtable_tables = context.bot_data.get('airtable_tables', {})

        if 'scans' not in airtable_tables:
            logger.error("Scans table not found in Airtable tables")
            await update.message.reply_text(get_message("failed_update", user_language))
            return

        stats = await get_today_stats(airtable_tables)
        current_time = get_israel_time().strftime("%H:%M")
        message_text = generate_message_text(stats, current_time, user_language)

        chat = update.effective_chat
        keyboard = await get_main_keyboard(user_language, chat, user, context)

        await context.bot.send_message(
            chat_id=user.id,
            text=message_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.exception(f"Error in send_update: {str(e)}")
        user_language = context.user_data.get('language', 'ru')
        await update.message.reply_text(get_message("failed_update", user_language).format(str(e)))

async def send_yesterday_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat

    if not await is_user_admin(chat, user, context):
        await update.message.reply_text("You don't have permission to access this information.")
        return

    try:
        user_language = context.user_data.get('language', 'ru')
        airtable_tables = context.bot_data.get('airtable_tables', {})

        if 'scans' not in airtable_tables:
            logger.error("Scans table not found in Airtable tables")
            await update.message.reply_text(get_message("failed_update", user_language))
            return

        stats = await get_yesterday_stats(airtable_tables)
        message_text = generate_yesterday_message_text(stats, user_language)

        keyboard = await get_main_keyboard(user_language, chat, user, context)

        await context.bot.send_message(
            chat_id=user.id,
            text=message_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.exception(f"Error in send_yesterday_update: {str(e)}")
        user_language = context.user_data.get('language', 'ru')
        await update.message.reply_text(get_message("failed_update", user_language).format(str(e)))

async def send_monthly_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        user_language = context.user_data.get('language', 'ru')
        airtable_tables = context.bot_data.get('airtable_tables', {})
        monthly_stats_cache = context.bot_data.get('monthly_stats_cache')

        if monthly_stats_cache:
            stats = await monthly_stats_cache.get_stats(airtable_tables)
        else:
            stats = await get_monthly_stats(airtable_tables)

        message_text = generate_monthly_message_text(stats, user_language)

        chat = update.effective_chat
        keyboard = await get_main_keyboard(user_language, chat, user, context)

        await context.bot.send_message(
            chat_id=user.id,
            text=message_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.exception(f"Error in send_monthly_update: {str(e)}")
        user_language = context.user_data.get('language', 'ru')
        await update.message.reply_text(get_message("failed_update", user_language).format(str(e)))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_language = context.user_data.get('language', 'ru')

    if query.data == "cars_today":
        await send_update(update, context)
    elif query.data == "cars_yesterday":
        await send_yesterday_update(update, context)
    elif query.data == "cars_month":
        await send_monthly_update(update, context)
    elif query.data == "language":
        message = get_message("select_language", user_language)
        await query.edit_message_text(
            text=message,
            reply_markup=get_language_menu(),
            parse_mode=ParseMode.HTML
        )

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
        message_text += f"   • Шлифовка: {stats['shlaif']}\n"
    elif user_language == "he":
        message_text = f"<b>סטטיסטיקה נכון ל-{current_time}:</b>\n\n"
        message_text += f"🚿 <b>נשטפו:</b> {stats['total_washed']}\n"
        message_text += f"   • שטיפה רגילה: {stats['normal_wash']}\n"
        message_text += f"   • ניקוי דבק: {stats['additional_cleaning']}\n"
        message_text += f"   • שטיפה קלה: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>הוברקו:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ חלקים: {stats['full_polish']}\n"
        message_text += f"   • 1-3 חלקים: {stats['half_polish']}\n"
        message_text += f"   • שלייף: {stats['shlaif']}\n"
    else:  # Default to English
        message_text = f"<b>Statistics as of {current_time}:</b>\n\n"
        message_text += f"🚿 <b>Washed:</b> {stats['total_washed']}\n"
        message_text += f"   • Regular wash: {stats['normal_wash']}\n"
        message_text += f"   • Glue cleaning: {stats['additional_cleaning']}\n"
        message_text += f"   • Light wash: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Polished:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ parts: {stats['full_polish']}\n"
        message_text += f"   • 1-3 parts: {stats['half_polish']}\n"
        message_text += f"   • Shlaif: {stats['shlaif']}\n"
    return message_text


def generate_yesterday_message_text(stats, user_language):
    if user_language == "ru":
        message_text = "<b>Статистика за вчера:</b>\n\n"
        message_text += f"🚿 <b>Помыто:</b> {stats['total_washed']}\n"
        message_text += f"   • Обычная мойка: {stats['normal_wash']}\n"
        message_text += f"   • Мойка с клеем: {stats['additional_cleaning']}\n"
        message_text += f"   • Легкая мойка: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Отполировано:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ деталей: {stats['full_polish']}\n"
        message_text += f"   • 1-3 детали: {stats['half_polish']}\n"
        message_text += f"   • Шлифовка: {stats['shlaif']}\n"
        message_text += f"\n💰 <b>Общая выручка:</b> {stats['revenue']} NIS"
    elif user_language == "he":
        message_text = "<b>סטטיסטיקה של אתמול:</b>\n\n"
        message_text += f"🚿 <b>נשטפו:</b> {stats['total_washed']}\n"
        message_text += f"   • שטיפה רגילה: {stats['normal_wash']}\n"
        message_text += f"   • ניקוי דבק: {stats['additional_cleaning']}\n"
        message_text += f"   • שטיפה קלה: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>הוברקו:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ חלקים: {stats['full_polish']}\n"
        message_text += f"   • 1-3 חלקים: {stats['half_polish']}\n"
        message_text += f"   • שלייף: {stats['shlaif']}\n"
        message_text += f"\n💰 <b>סך ההכנסות:</b> {stats['revenue']} NIS"
    else:  # Default to English
        message_text = "<b>Yesterday's statistics:</b>\n\n"
        message_text += f"🚿 <b>Washed:</b> {stats['total_washed']}\n"
        message_text += f"   • Regular wash: {stats['normal_wash']}\n"
        message_text += f"   • Wash and glue cleaning: {stats['additional_cleaning']}\n"
        message_text += f"   • Light wash: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Polished:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ parts: {stats['full_polish']}\n"
        message_text += f"   • 1-3 parts: {stats['half_polish']}\n"
        message_text += f"   • Shlaif: {stats['shlaif']}\n"
        message_text += f"\n💰 <b>Total revenue:</b> {stats['revenue']} NIS"
    return message_text


def generate_monthly_message_text(stats, user_language):
    if not stats["on_track"]:
        deviation_text = {
            "ru": f"На сегодня вы отстаете от цели на {abs(stats['deviation'])} автомобилей.",
            "he": f"אתם בפיגור של {abs(stats['deviation'])} רכבים מהיעד.",
            "en": f"You are behind the target by {abs(stats['deviation'])} cars.",
        }
        suggestion_text = {
            "ru": f"Чтобы достичь цели, необходимо мыть примерно {stats['required_daily_cars']} автомобилей в день.",
            "he": f"כדי להגיע ליעד, יש לטפל בכ-{stats['required_daily_cars']} רכבים ביום.",
            "en": f"To reach the goal, you need to process approximately {stats['required_daily_cars']} cars per day.",
        }
    else:
        deviation_text = {
            "ru": f"Вы опережаете цель на {stats['deviation']} автомобилей.",
            "he": f"אתם מקדימים את היעד ב-{stats['deviation']} רכבים.",
            "en": f"You are ahead of the target by {stats['deviation']} cars.",
        }
        suggestion_text = {
            "ru": "Продолжайте в том же духе!",
            "he": "תמשיכו כך!",
            "en": "Keep up the good work!",
        }

    lang = user_language if user_language in ["ru", "he"] else "en"

    message_text = ""
    if lang == "ru":
        message_text += "<b>Статистика за текущий месяц:</b>\n\n"
        message_text += (
            f"{stats['progress_symbol']} <b>Прогресс:</b> {stats['total_washed']} из "
            f"{stats['current_target']} (Цель: {stats['total_goal']})\n"
        )
        message_text += f"{deviation_text[lang]}\n"
        message_text += f"{suggestion_text[lang]}\n\n"
        message_text += f"🚿 <b>Помыто:</b> {stats['total_washed']}\n"
        message_text += f"   • Обычная мойка: {stats['normal_wash']}\n"
        message_text += f"   • Мойка с клеем: {stats['additional_cleaning']}\n"
        message_text += f"   • Легкая мойка: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Отполировано:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ деталей: {stats['full_polish']}\n"
        message_text += f"   • 1-3 детали: {stats['half_polish']}\n"
        message_text += f"   • Шлайф: {stats['shlaif']}\n\n"
        message_text += f"💰 <b>Общая выручка:</b> {stats['total_revenue']} NIS\n"
        message_text += f"   • Мойка: {stats['wash_revenue']} NIS\n"
        message_text += f"   • Полировка: {stats['polish_revenue']} NIS\n"
    elif lang == "he":
        message_text += "<b>סטטיסטיקה של החודש הנוכחי:</b>\n\n"
        message_text += (
            f"{stats['progress_symbol']} <b>התקדמות:</b> {stats['total_washed']} מתוך "
            f"{stats['current_target']} (יעד: {stats['total_goal']})\n"
        )
        message_text += f"{deviation_text[lang]}\n"
        message_text += f"{suggestion_text[lang]}\n\n"
        message_text += f"🚿 <b>נשטפו:</b> {stats['total_washed']}\n"
        message_text += f"   • שטיפה רגילה: {stats['normal_wash']}\n"
        message_text += f"   • ניקוי דבק: {stats['additional_cleaning']}\n"
        message_text += f"   • שטיפה קלה: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>הוברקו:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ חלקים: {stats['full_polish']}\n"
        message_text += f"   • 1-3 חלקים: {stats['half_polish']}\n"
        message_text += f"   • שלייף: {stats['shlaif']}\n\n"
        message_text += f"💰 <b>סך ההכנסות:</b> {stats['total_revenue']} NIS\n"
        message_text += f"   • שטיפה: {stats['wash_revenue']} NIS\n"
        message_text += f"   • הברקה: {stats['polish_revenue']} NIS\n"
    else:  # Default to English
        message_text += "<b>Statistics for the current month:</b>\n\n"
        message_text += (
            f"{stats['progress_symbol']} <b>Progress:</b> {stats['total_washed']} out of "
            f"{stats['current_target']} (Goal: {stats['total_goal']})\n"
        )
        message_text += f"{deviation_text[lang]}\n"
        message_text += f"{suggestion_text[lang]}\n\n"
        message_text += f"🚿 <b>Washed:</b> {stats['total_washed']}\n"
        message_text += f"   • Regular wash: {stats['normal_wash']}\n"
        message_text += f"   • Wash and glue cleaning: {stats['additional_cleaning']}\n"
        message_text += f"   • Light wash: {stats['light_wash']}\n\n"
        message_text += f"✨ <b>Polished:</b> {stats['total_polished']}\n"
        message_text += f"   • 4+ parts: {stats['full_polish']}\n"
        message_text += f"   • 1-3 parts: {stats['half_polish']}\n"
        message_text += f"   • Shlaif: {stats['shlaif']}\n\n"
        message_text += f"💰 <b>Total revenue:</b> {stats['total_revenue']} NIS\n"
        message_text += f"   • Wash: {stats['wash_revenue']} NIS\n"
        message_text += f"   • Polish: {stats['polish_revenue']} NIS\n"
    return message_text


def combine_stats(cached_stats: dict, today_stats: dict) -> dict:
    combined = cached_stats.copy()
    fields_to_sum = [
        "total_washed",
        "normal_wash",
        "additional_cleaning",
        "light_wash",
        "total_polished",
        "full_polish",
        "half_polish",
        "shlaif",
        "wash_revenue",
        "polish_revenue",
        "total_revenue"
    ]

    for field in fields_to_sum:
        combined[field] += today_stats.get(field, 0)

    combined['total_washed'] += today_stats.get('total_washed', 0)
    combined['wash_revenue'] += today_stats.get('wash_revenue', 0)
    combined['polish_revenue'] += today_stats.get('polish_revenue', 0)
    combined['total_revenue'] = combined['wash_revenue'] + combined['polish_revenue']

    combined['deviation'] = combined['total_washed'] - combined['current_target']

    combined['remaining_workdays'] = max(combined['remaining_workdays'] - 1, 0)

    cars_needed = combined['total_goal'] - combined['total_washed']
    combined['required_daily_cars'] = int(cars_needed / combined['remaining_workdays']) if combined['remaining_workdays'] > 0 else 0

    combined['on_track'] = combined['total_washed'] >= combined['current_target']
    combined['progress_symbol'] = "🟢" if combined['on_track'] else "🔴"

    return combined

