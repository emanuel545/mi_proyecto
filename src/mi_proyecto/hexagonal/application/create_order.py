from dataclasses import dataclass

from mi_proyecto.hexagonal.application.ports import (NotificationPort,
                                                     OrderRepository)
from mi_proyecto.hexagonal.domain.order import Order, OrderItem


@dataclass
class OrderItemDTO:
    product: str
    quantity: int
    unit_price: float


@dataclass
class CreateOrderCommand:
    customer: str
    items: list[OrderItemDTO]


class CreateOrderUseCase:
    def __init__(
        self,
        repository: OrderRepository,
        notifier: NotificationPort,
    ) -> None:
        self.repository = repository
        self.notifier = notifier

    def execute(self, command: CreateOrderCommand) -> Order:
        if not command.customer:
            raise ValueError("El cliente es obligatorio")

        if not command.items:
            raise ValueError("La orden debe tener al menos un producto")

        items = [
            OrderItem(
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in command.items
        ]

        for item in items:
            if item.quantity <= 0:
                raise ValueError("La cantidad debe ser mayor a cero")

            if item.unit_price <= 0:
                raise ValueError("El precio unitario debe ser mayor a cero")

        order = Order(customer=command.customer, items=items)

        self.repository.save(order)
        self.notifier.notify_order_created(order)

        return order
