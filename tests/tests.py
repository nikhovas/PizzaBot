from tests.helpers import *
import pytest


class TestOrder:
    def test_default_dialog(self):
        loop = asyncio.get_event_loop()
        sender = DemoMessageSender()
        kernel = DemoKernel()

        @asyncio.coroutine
        async def do_test():
            order = Order(sender, kernel)

            await order.proceed('asdf')

            msg = sender.queue.get_nowait()
            assert msg == 'Какую вы хотите пиццу? Большую или маленькую?'
            await order.proceed('большую')

            msg = sender.queue.get_nowait()
            assert msg == 'Как вы будете платить?'
            await order.proceed('картой')

            msg = sender.queue.get_nowait()
            assert msg == 'Вы хотите большую пиццу, оплата - картой?'
            await order.proceed('да')

            msg = sender.queue.get_nowait()
            assert msg == 'Спасибо за заказ!'
            msg = sender.queue.get_nowait()
            assert msg == 'Для следующего заказа напишите любое слово.'

            order_in_database = kernel.database.queue.get_nowait()

        loop.run_until_complete(do_test())

    def test_incorrect_input(self):
        loop = asyncio.get_event_loop()
        sender = DemoMessageSender()
        kernel = DemoKernel()

        @asyncio.coroutine
        async def do_test():
            order = Order(sender, kernel)

            await order.proceed('asdf')

            msg = sender.queue.get_nowait()
            assert msg == 'Какую вы хотите пиццу? Большую или маленькую?'
            await order.proceed('sadfasd')

            msg = sender.queue.get_nowait()
            assert msg == 'Текст не распознан, напишите еще раз'
            msg = sender.queue.get_nowait()
            assert msg == 'Какую вы хотите пиццу? Большую или маленькую?'

        loop.run_until_complete(do_test())

    def test_timeout(self):
        import src.Order
        src.Order.TIMEOUT = 2

        loop = asyncio.get_event_loop()
        sender = DemoMessageSender()
        kernel = DemoKernel()

        @asyncio.coroutine
        async def do_test():
            order = Order(sender, kernel)

            await order.proceed('asdf')
            await asyncio.sleep(3, loop=loop)

            msg = sender.queue.get_nowait()
            assert msg == 'Какую вы хотите пиццу? Большую или маленькую?'
            msg = sender.queue.get_nowait()
            assert msg == 'Истекло время ожидания.'
            msg = sender.queue.get_nowait()
            assert msg == 'Для следующего заказа напишите любое слово.'

        loop.run_until_complete(do_test())



