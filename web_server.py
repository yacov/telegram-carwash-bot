from quart import Quart, request, jsonify
import os
import asyncio
from bot import Bot
from dotenv import load_dotenv
import logging
from telegram import Update

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Quart(__name__)

# Initialize bot
bot_instance = Bot(
    token="6860364776:AAEF-X-aFT__wy3KffYstEVQnIfi-QIrdLU",
    chat_id=os.getenv('CHAT_ID'),
    webhook_url="https://lubinskybot-7a6538f13148.herokuapp.com/webhook"
)

@app.route('/', methods=['GET'])
async def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    logger.info("Received webhook call")
    if request.headers.get('content-type') == 'application/json':
        update = Update.de_json(await request.get_json(), bot_instance.application.bot)
        logger.info(f"Received update: {update}")
        await bot_instance.process_update(update)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid content type"}), 400

async def run_bot():
    await bot_instance.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Run the bot setup asynchronously
    asyncio.run(run_bot())
    # Run the Quart app
    app.run(host='0.0.0.0', port=port)
