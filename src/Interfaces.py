from abc import ABC
from src import OrderDetails


class DatabaseInterface(ABC):
    async def add_order(self, size: OrderDetails.PizzaSizes, payment: OrderDetails.PaymentTypes):
        pass


class MessageSender(ABC):
    async def send_message(self, msg: str, buttons=None):
        pass

    def end_dialog(self):
        pass


class MessengerInterface(ABC):
    def start_listening(self):
        pass

    def start_webhook(self, webhook_path: str, webapp_host: str, webapp_port: int, webhook_url: str):
        pass

    def webhook_enabled(self) -> bool:
        pass
