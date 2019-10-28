import os
from dotenv import load_dotenv
"""
Loads necessary variables for using Twitter API
"""
# initialize keys from env
load_dotenv()
# retrieve keys from environment variables
consumer_key = os.environ.get('TWBOT_CON_KEY')
consumer_secret = os.environ.get('TWBOT_CON_SECRET')
access_token = os.environ.get('TWBOT_ACCESS_TOKEN')
access_secret = os.environ.get('TWBOT_ACCESS_SECRET')
handle = os.environ.get('TWBOT_HANDLE')