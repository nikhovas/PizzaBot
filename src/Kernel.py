import sys

import config
from src.Interfaces import MessengerInterface, DatabaseInterface


class Kernel:
    messenger: MessengerInterface
    database: DatabaseInterface

    def __init__(self):
        from src.Messengers.Telegram import TelegramMessenger
        self.messenger = TelegramMessenger(self, config.TOKEN)

        from src.Database import Database
        self.database = Database(self)

    def run(self):
        if config.MODE == "dev":
            self.messenger.start_listening()
        elif config.MODE == "prod":
            self.messenger.start_webhook(f"/{config.TOKEN}", "0.0.0.0", config.PORT,
                                         f"https://{config.HEROKU_APP_NAME}.herokuapp.com/{config.TOKEN}")
        else:
            print("no mode")
            sys.exit(1)
