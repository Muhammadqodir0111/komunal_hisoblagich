import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL')

BOT_API_USERNAME = os.getenv('BOT_API_USERNAME')
BOT_API_PASSWORD = os.getenv('BOT_API_PASSWORD')