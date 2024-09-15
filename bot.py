import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, TypeHandler
from dotenv import load_dotenv
from datetime import time

from database import init_airtable_tables
from handlers import start_command, language_command, set_language_callback, send_update, handle_callback, send_yesterday_update, send_monthly_update
from scheduler import schedule_daily_report
from utils import is_user_admin
from cache import MonthlyStatsCache 

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class Bot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.application = None
        self.airtable_tables = None 
        self.monthly_stats_cache = MonthlyStatsCache()
    
    async def initialize_cache(self):
        await self.monthly_stats_cache.get_stats(self.airtable_tables, force_refresh=True)
        self.application.job_queue.run_daily(
            self.monthly_stats_cache.update_daily,
            time=time(hour=0, minute=0),
            data={'airtable_tables': self.airtable_tables}
        )

    def start(self):
        try:
            self.application = (
                ApplicationBuilder()
                .token(self.token)
                .build()
            )

            self.airtable_tables = init_airtable_tables()
            self.application.bot_data['airtable_tables'] = self.airtable_tables
            logger.info("Airtable tables initialized and stored in bot_data")

            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.initialize_cache())
            logger.info("Monthly stats cache initialized")

            # Add handlers
            self.application.add_handler(TypeHandler(Update, self.pre_process_update), group=-1)
            self.application.add_handler(CommandHandler("start", start_command))
            self.application.add_handler(CommandHandler("language", language_command))
            self.application.add_handler(CallbackQueryHandler(set_language_callback, pattern="^set_language"))
            self.application.add_handler(CallbackQueryHandler(handle_callback))
            self.application.add_handler(CommandHandler("cars", send_update))
            self.application.add_handler(CommandHandler("yesterday", send_yesterday_update))
            self.application.add_handler(CallbackQueryHandler(send_yesterday_update, pattern="^cars_yesterday$"))
            self.application.add_handler(CommandHandler("month", send_monthly_update))
            self.application.bot_data['monthly_stats_cache'] = self.monthly_stats_cache

            # Add error handler
            self.application.add_error_handler(self.error_handler)

            # Schedule daily report
            schedule_daily_report(self.application, self.chat_id)

            logger.info("Bot started. Press Ctrl+C to stop.")
            
            # Start the bot using run_polling
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Failed to run the bot: {e}", exc_info=True)

    async def pre_process_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Pre-process all updates before they reach other handlers."""
        if update.effective_user:
            user_id = update.effective_user.id
            if 'user_languages' in context.bot_data and user_id in context.bot_data['user_languages']:
                context.user_data['language'] = context.bot_data['user_languages'][user_id]
            else:
                context.user_data['language'] = context.user_data.get('language', 'ru')
        # Add more pre-processing logic as needed

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error("Exception while handling an update:", exc_info=context.error)
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("An error occurred. Please try again later.")

def main():
    bot = Bot(token="6860364776:AAEF-X-aFT__wy3KffYstEVQnIfi-QIrdLU", chat_id=os.getenv('CHAT_ID'))
    bot.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
