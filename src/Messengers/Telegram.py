from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio

from aiogram.utils.executor import start_webhook

from src.Interfaces import MessengerInterface, MessageSender
from src.Order import Order
from src.Kernel import Kernel

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class TelegramDialog(MessageSender):
    def __init__(self, chat_id: int, bot: Bot, chats: dict):
        self.chat_id = chat_id
        self.bot = bot
        self.chats = chats

    async def send_message(self, msg: str, buttons=None):
        if buttons is None:
            await self.bot.send_message(self.chat_id, msg)
        else:
            tele_buttons = []
            for i in buttons:
                tele_buttons.append(KeyboardButton(i))

            markup = ReplyKeyboardMarkup(resize_keyboard=True).row(*tele_buttons)
            await self.bot.send_message(self.chat_id, msg, reply_markup=markup)

    def end_dialog(self):
        try:
            del self.chats[self.chat_id]
        except ...:
            pass


class TelegramMessenger(MessengerInterface):

    def __init__(self, kernel: Kernel, token: str):
        self.bot = Bot(token=token)
        self.dispatcher = Dispatcher(self.bot, storage=MemoryStorage())
        self.chat_dict = dict()
        self.dispatcher.register_message_handler(self.handler)
        self.kernel = kernel
        self.webhook_url = ''

    def start_listening(self):
        executor.start_polling(self.dispatcher)

    async def handler(self, message: types.Message):
        order = self.chat_dict.get(message.chat.id)
        if order is None:
            order = Order(TelegramDialog(message.chat.id, self.bot, self.chat_dict), self.kernel)
            self.chat_dict[message.chat.id] = order
        # asyncio.get_event_loop().create_task(order.proceed(message.text))
        await order.proceed(message.text)


    async def on_startup(self, dp):
        await self.bot.set_webhook(self.webhook_url)

    async def on_shutdown(self, dp):
        await self.bot.delete_webhook()

    def start_webhook(self, webhook_path: str, webapp_host: str, webapp_port: int, webhook_url: str):
        self.webhook_url = webhook_url
        start_webhook(
            dispatcher=self.dispatcher,
            webhook_path=webhook_path,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown,
            skip_updates=True,
            host=webapp_host,
            port=webapp_port,
        )
