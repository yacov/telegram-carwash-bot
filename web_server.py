from flask import Flask, request, jsonify
import os
import asyncio
from bot import Bot
from dotenv import load_dotenv
import logging
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
    webhook_url="https://curvy-steaks-stand.loca.lt/webhook"
)

@app.route('/', methods=['GET'])
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Received webhook call")
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = request.get_json()
            logger.info(f"Received update: {update}")
            asyncio.run(bot_instance.process_update(update))
            return 'ok', 200
        else:
            logger.warning("Received non-JSON content")
            return 'Error: expected JSON data', 400
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
        return 'Error processing update', 500

async def init_bot():
    await bot_instance.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    # Initialize bot before starting the Flask server
    asyncio.run(init_bot())
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port)
