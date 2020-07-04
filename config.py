import os

TIMEOUT = 10
LOCAL_TOKEN = ''

TOKEN = os.getenv("TOKEN", LOCAL_TOKEN)
MODE = os.getenv("MODE", "dev")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
