from flask import Flask, request, jsonify
import os
import asyncio
from bot import Bot
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import Application

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Initialize bot
bot_instance = Bot(
    token="6860364776:AAEF-X-aFT__wy3KffYstEVQnIfi-QIrdLU",
    chat_id=os.getenv('CHAT_ID'),
    webhook_url="https://lubinskybot-7a6538f13148.herokuapp.com/webhook"
)

@app.route('/', methods=['GET'])
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Received webhook call")
    if request.headers.get('content-type') == 'application/json':
        update = Update.de_json(request.get_json(), bot_instance.application.bot)
        logger.info(f"Received update: {update}")
        asyncio.run(bot_instance.process_update(update))
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid content type"}), 400

def run_bot():
    asyncio.run(bot_instance.start())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    run_bot()
    app.run(host='0.0.0.0', port=port)
