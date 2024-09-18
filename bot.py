import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, TypeHandler
from dotenv import load_dotenv
from datetime import time
import asyncio
from database import init_airtable_tables
from handlers import start_command, language_command, set_language_callback, send_update, handle_callback, send_yesterday_update, send_monthly_update
from scheduler import schedule_daily_report
from utils import is_user_admin
from cache import MonthlyStatsCache

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

load_dotenv()

class Bot:
    def __init__(self, token, chat_id, webhook_url):
        self.token = token
        self.chat_id = chat_id
        self.webhook_url = webhook_url
        self.application = Application.builder().token(self.token).build()
        self.monthly_stats_cache = MonthlyStatsCache()
        self.is_initialized = False

    async def initialize_cache(self):
        await self.monthly_stats_cache.get_stats(self.airtable_tables, force_refresh=True)
        self.application.job_queue.run_daily(
            self.monthly_stats_cache.update_daily,
            time=time(hour=0, minute=0),
            data={'airtable_tables': self.airtable_tables}
        )

    async def start(self):
        # Add handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("language", language_command))
        self.application.add_handler(CallbackQueryHandler(set_language_callback, pattern="^set_language"))
        self.application.add_handler(CallbackQueryHandler(handle_callback))
        self.application.add_handler(CommandHandler("cars", send_update))
        self.application.add_handler(CommandHandler("yesterday", send_yesterday_update))
        self.application.add_handler(CallbackQueryHandler(send_yesterday_update, pattern="^cars_yesterday$"))
        self.application.add_handler(CommandHandler("month", send_monthly_update))

        # Initialize other components
        self.airtable_tables = init_airtable_tables()
        self.application.bot_data['airtable_tables'] = self.airtable_tables
        await self.initialize_cache()
        schedule_daily_report(self.application, self.chat_id)

        # Set up webhook
        await self.application.bot.set_webhook(url=self.webhook_url)
        logger.info(f"Webhook set to: {self.webhook_url}")

        # Initialize the application
        await self.application.initialize()
        self.is_initialized = True

    async def pre_process_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Pre-process all updates before they reach other handlers."""
        if update.effective_user:
            user_id = update.effective_user.id
            if 'user_languages' in context.bot_data and user_id in context.bot_data['user_languages']:
                context.user_data['language'] = context.bot_data['user_languages'][user_id]
            else:
                context.user_data['language'] = context.user_data.get('language', 'ru')

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error("Exception while handling an update:", exc_info=context.error)
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("An error occurred. Please try again later.")

    async def process_update(self, update_data):
        if not self.is_initialized:
            logger.error("Attempted to process update before bot was initialized")
            return

        try:
            await asyncio.wait_for(
                self.application.process_update(Update.de_json(update_data, self.application.bot)),
                timeout=10  # Adjust this value as needed
            )
        except asyncio.TimeoutError:
            logger.error("Update processing timed out")

