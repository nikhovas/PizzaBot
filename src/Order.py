from transitions.extensions.states import add_state_features

from src.Interfaces import MessageSender
from transitions.extensions.asyncio import AsyncMachine, AsyncTimeout
import asyncio

from src.Kernel import Kernel
from src.OrderDetails import *


TIMEOUT = 2


@add_state_features(AsyncTimeout)
class CustomStateMachine(AsyncMachine):
    pass


class Order:
    def __del__(self):
        print("here")

    def __init__(self, dialog: MessageSender, kernel: Kernel):
        states = [
            dict(name='initial_in', timeout=TIMEOUT, on_timeout='timeout_trigger'),
            dict(name='initial_out'),
            dict(name='selection_in', timeout=TIMEOUT, on_timeout='timeout_trigger'),
            dict(name='selection_out'),
            dict(name='payment_in', timeout=TIMEOUT, on_timeout='timeout_trigger'),
            dict(name='payment_out'),
            dict(name='check_in', timeout=TIMEOUT, on_timeout='timeout_trigger'),
            dict(name='check_out'),
            dict(name='order_sent'),
            dict(name='another_request'),
            dict(name='timeout_order')
        ]

        transitions = [
            dict(
                trigger="proceed",
                source='initial_in',
                dest='initial_out',
                before=self.message_initial_stage,
                after=self.after_stage
            ),
            dict(
                trigger="go",
                source='initial_out',
                dest='selection_in',
                before=self.to_selection_stage
            ),


            dict(
                trigger="proceed",
                source='selection_in',
                dest='selection_out',
                before=self.message_selection_stage,
                after=self.after_stage
            ),
            dict(
                trigger="go",
                source='selection_out',
                dest='payment_in',
                before=[self.send_error_parse_message, self.to_selection_stage],
                conditions='parse_error'
            ),


            dict(
                trigger="go",
                source='selection_out',
                dest='payment_in',
                before=self.to_payment_stage,
                unless='parse_error'
            ),
            dict(
                trigger="proceed",
                source='payment_in',
                dest='payment_out',
                before=self.message_payment_stage,
                after=self.after_stage
            ),
            dict(
                trigger="go",
                source='payment_out',
                dest='payment_in',
                before=[self.send_error_parse_message, self.to_payment_stage],
                conditions='parse_error'
            ),


            dict(
                trigger="go",
                source='payment_out',
                dest='check_in',
                before="to_check_stage",
                unless='parse_error'
            ),
            dict(
                trigger="proceed",
                source='check_in',
                dest='check_out',
                before=self.message_check_stage,
                after=self.after_stage
            ),
            dict(
                trigger="go",
                source='check_out',
                dest='check_in',
                 before=[self.send_error_parse_message, self.to_check_stage],
                conditions='parse_error'
            ),

            # if not confirmed
            dict(trigger="go",
                 source='check_out',
                 dest='selection_in',
                 before=self.to_selection_stage,
                 unless='is_confirmed'
            ),

            # if confirmed
            dict(
                trigger="go",
                source='check_out',
                dest='order_sent',
                before=self.to_order_sent_state,
                after=self.after_stage,
                conditions='is_confirmed'
            ),

            dict(
                trigger="go",
                source='order_sent',
                dest='another_request',
                before=self.to_another_request_state,
            ),

            dict(
                trigger="timeout_trigger",
                source='*',
                dest='timeout_order',
                before=self.timeout_handler,
                after=self.after_stage
            ),
            dict(
                trigger="go",
                source='timeout_order',
                dest='another_request',
                before=self.to_another_request_state,
            ),
        ]

        self.machine = CustomStateMachine(self, states=states, transitions=transitions, initial='initial_in')
        self.dialog = dialog
        self.pizza_size = None
        self.payment_type = None
        self.is_confirmed = False
        self.parse_error = False
        self.kernel = kernel

    async def message_initial_stage(self, msg: str):
        pass

    async def to_selection_stage(self):
        self.parse_error = False
        await self.dialog.send_message("Какую вы хотите пиццу? Большую или маленькую?", ['большую', 'маленькую'])

    async def message_selection_stage(self, msg: str):
        msg = msg.lower()
        if msg.startswith('больш'):
            self.pizza_size = PizzaSizes.BIG
        elif msg.startswith('маленьк'):
            self.pizza_size = PizzaSizes.SMALL
        else:
            self.parse_error = True

    async def to_payment_stage(self):
        self.parse_error = False
        await self.dialog.send_message("Как вы будете платить?", ['картой', 'наличными'])

    async def message_payment_stage(self, msg: str):
        msg = msg.lower()
        if "карт" in msg:
            self.payment_type = PaymentTypes.CARD
        elif "нал" in msg:
            self.payment_type = PaymentTypes.CASH
        else:
            self.parse_error = True

    async def to_check_stage(self):
        self.parse_error = False
        msg = f"Вы хотите {'большую' if self.pizza_size == PizzaSizes.BIG else 'маленькую'} пиццу, оплата - " \
              f"{'наличкой' if self.payment_type == PaymentTypes.CASH else 'картой'}?"
        await self.dialog.send_message(msg, ['да', 'нет'])

    async def message_check_stage(self, msg: str):
        msg = msg.lower()
        if msg == "да":
            self.is_confirmed = True
        elif msg == "нет":
            self.is_confirmed = False
        else:
            self.parse_error = True

    async def to_order_sent_state(self):
        await self.kernel.database.add_order(self.pizza_size, self.payment_type)
        await self.dialog.send_message('Спасибо за заказ!')

    async def to_another_request_state(self):
        await self.dialog.send_message('Для следующего заказа напишите любое слово.', ['новый заказ'])
        del self.machine
        self.dialog.end_dialog()

    async def send_error_parse_message(self):
        await self.dialog.send_message("Текст не распознан, напишите еще раз")

    async def after_stage(self, *args):
        # asyncio.get_event_loop().create_task(self.go())
        await self.go()


    async def timeout_handler(self):
        await self.dialog.send_message('Истекло время ожидания.')
