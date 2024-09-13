import os
import logging
import asyncio
import signal

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, Defaults
from dotenv import load_dotenv

from database import init_airtable_tables
from handlers import start_command, language_command, set_language_callback, send_update, handle_callback, send_yesterday_update
from scheduler import schedule_daily_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

load_dotenv()

class Bot:
    def __init__(self, token, chat_id):
        """
        Initialize the Bot class with token and chat_id.
        
        :param token: Bot token for authentication
        :param chat_id: Chat ID for sending messages
        """
        self.token = token
        self.chat_id = chat_id
        self.application = None
        self.airtable_tables = None  # Add this line

    async def start(self):
        """
        Start the bot, initialize handlers, and begin polling for updates.
        """
        try:
            defaults = Defaults(parse_mode="HTML")
            self.application = Application.builder().token(self.token).defaults(defaults).build()

            # Initialize Airtable tables
            self.airtable_tables = init_airtable_tables()
            self.application.bot_data['airtable_tables'] = self.airtable_tables
            logger.info("Airtable tables initialized and stored in bot_data")

            # Add handlers
            self.application.add_handler(CommandHandler("start", start_command))
            self.application.add_handler(CommandHandler("language", language_command))
            self.application.add_handler(CallbackQueryHandler(set_language_callback, pattern="^set_language"))
            self.application.add_handler(CallbackQueryHandler(handle_callback))
            self.application.add_handler(CommandHandler("cars", send_update))
            self.application.add_handler(CommandHandler("yesterday", send_yesterday_update))
            self.application.add_handler(CallbackQueryHandler(send_yesterday_update, pattern="^cars_yesterday$"))

            # Add error handler
            self.application.add_error_handler(self.error_handler)

            # Schedule daily report
            schedule_daily_report(self.application, self.chat_id)

            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            logger.info("Bot started. Press Ctrl+C to stop.")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Bot is shutting down...")
        except Exception as e:
            logger.error(f"Failed to run the bot: {e}")
        finally:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle errors that occur during the execution of handlers.

        :param update: The update that caused the error
        :param context: The context object containing error details
        """
        try:
            logger.error(f"Exception while handling an update: {context.error}", exc_info=True)  # Update this line
            if isinstance(update, Update) and update.effective_message:
                await update.effective_message.reply_text("An error occurred. Please try again later.")
        except Exception as e:
            logger.exception(f"Error while sending error message: {e}")

def shutdown_handler(*args):
    """
    Handle graceful shutdown on SIGINT.
    """
    if bot.application:
        asyncio.create_task(bot.application.stop())

async def main():
    """
    Main function to run the bot.
    """
    global bot
    bot = Bot(token="6860364776:AAEF-X-aFT__wy3KffYstEVQnIfi-QIrdLU", chat_id=os.environ.get('CHAT_ID'))
    
    # Register shutdown handler
    signal.signal(signal.SIGINT, shutdown_handler)
    
    await bot.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
