import os
from dotenv import load_dotenv

load_dotenv()
MONGO_CONNECTION_STRING = os.environ.get('MONGO_CONNECTION_STRING')
MEANING_CLOUD_KEY = os.environ.get('MEANING_CLOUD_KEY')
PARALLEL_DOTS_KEY = os.environ.get('PARALLEL_DOTS_KEY')
PARALLEL_DOTS_KEY_2 = os.environ.get('PARALLEL_DOTS_KEY_2')
