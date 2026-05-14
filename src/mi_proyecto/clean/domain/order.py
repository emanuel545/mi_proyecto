from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class DomainEvent:
    pass


@dataclass
class OrderCreated(DomainEvent):
    order_id: str
    customer: str
    total: float


@dataclass
class OrderItem:
    product: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    customer: str
    items: list[OrderItem]
    id: str = field(default_factory=lambda: str(uuid4()))
    events: list[DomainEvent] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    @classmethod
    def create(cls, customer: str, items: list[OrderItem]) -> "Order":
        if not customer:
            raise ValueError("El cliente es obligatorio")

        if not items:
            raise ValueError("La orden debe tener al menos un producto")

        for item in items:
            if item.quantity <= 0:
                raise ValueError("La cantidad debe ser mayor a cero")

            if item.unit_price <= 0:
                raise ValueError("El precio unitario debe ser mayor a cero")

        order = cls(customer=customer, items=items)

        order.events.append(
            OrderCreated(
                order_id=order.id,
                customer=order.customer,
                total=order.total,
            )
        )

        return order
