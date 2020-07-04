import asyncio
import os
import sys

from src.Interfaces import MessengerInterface, DatabaseInterface


class Kernel:
    messenger: MessengerInterface
    database: DatabaseInterface

    def __init__(self):
        from src.Messengers.Telegram import TelegramMessenger
        token = os.getenv("TOKEN")
        self.messenger = TelegramMessenger(self, token)

        from src.Database import Database
        self.database = Database(self)

    def run(self):
        mode = os.getenv("MODE")
        token = os.getenv("TOKEN")

        if mode == "dev":
            asyncio.get_event_loop().create_task(self.messenger.start_listening())
        elif mode == "prod":
            port = int(os.environ.get("PORT", "8443"))
            heroku_app_name = os.environ.get("HEROKU_APP_NAME")
            self.messenger.start_webhook(f"/{token}", "0.0.0.0", port, f"https://{heroku_app_name}.herokuapp.com/{token}")
        else:
            print("no mode")
            sys.exit(1)
