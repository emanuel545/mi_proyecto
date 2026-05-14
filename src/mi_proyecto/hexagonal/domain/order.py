from dataclasses import dataclass, field
from uuid import uuid4


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

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)
