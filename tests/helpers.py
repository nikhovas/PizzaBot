import asyncio
from src import OrderDetails
from src.Interfaces import MessageSender, DatabaseInterface
from src.Order import Order


class DemoMessageSender(MessageSender):
    def __init__(self):
        self.queue = asyncio.Queue()
        self.ended = False

    async def send_message(self, msg: str, buttons=None):
        await self.queue.put(msg)

    def end_dialog(self):
        self.ended = True


class DemoDatabase(DatabaseInterface):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def add_order(self, size: OrderDetails.PizzaSizes, payment: OrderDetails.PaymentTypes):
        await self.queue.put((size, payment))


class DemoKernel:
    def __init__(self):
        self.database = DemoDatabase()

    def run(self):
        pass
