from src import OrderDetails
from src.Interfaces import DatabaseInterface
from src.Kernel import Kernel


class Database(DatabaseInterface):
    def __init__(self, kernel: Kernel):
        self.kernel = kernel

    async def add_order(self, size: OrderDetails.PizzaSizes, payment: OrderDetails.PaymentTypes):
        print(f"Размер: {'большая' if size == OrderDetails.PizzaSizes.BIG else 'маленькая'}, "
              f"оплата: {'наличными' if payment == OrderDetails.PaymentTypes.CASH else 'картой'}")
