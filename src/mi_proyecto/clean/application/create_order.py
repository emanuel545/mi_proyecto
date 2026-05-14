from dataclasses import dataclass

from mi_proyecto.clean.application.ports import EventPublisher, UnitOfWork
from mi_proyecto.clean.domain.order import Order, OrderItem


@dataclass
class OrderItemInput:
    product: str
    quantity: int
    unit_price: float


@dataclass
class CreateOrderInput:
    customer: str
    items: list[OrderItemInput]


@dataclass
class CreateOrderOutput:
    id: str
    customer: str
    total: float


class CreateOrderUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        publisher: EventPublisher,
    ) -> None:
        self.uow = uow
        self.publisher = publisher

    def execute(self, input_data: CreateOrderInput) -> CreateOrderOutput:
        try:
            items = [
                OrderItem(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in input_data.items
            ]

            order = Order.create(
                customer=input_data.customer,
                items=items,
            )

            self.uow.orders.save(order)
            self.uow.commit()

            for event in order.events:
                self.publisher.publish(event)

            return CreateOrderOutput(
                id=order.id,
                customer=order.customer,
                total=order.total,
            )

        except Exception:
            self.uow.rollback()
            raise
