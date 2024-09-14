import os
from dotenv import load_dotenv

load_dotenv()

# Load admin usernames from environment variable
ADMIN_USERNAMES = [username.strip() for username in os.getenv('ADMIN_USERNAMES', '').split(',') if username.strip()]

def is_user_admin(username: str) -> bool:
    return True
