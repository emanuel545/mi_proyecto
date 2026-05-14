from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


class OrderData(TypedDict):
    order_id: int
    customer: str
    product: str
    quantity: int
    unit_price: float


@dataclass(order=True)
class Order:
    total: float = field(init=False, compare=True)
    order_id: int = field(compare=False)
    customer: str = field(compare=False)
    product: str = field(compare=False)
    quantity: int = field(compare=False)
    unit_price: float = field(compare=False)

    def __post_init__(self) -> None:
        self.total = self.quantity * self.unit_price

    def __str__(self) -> str:
        return (
            f"Orden #{self.order_id} | Cliente: {self.customer} | "
            f"Producto: {self.product} | Total: ${self.total:.2f}"
        )

    def apply_discount(self, percent: float) -> float:
        discount = self.total * (percent / 100)
        self.total -= discount
        return self.total


class OrderIn(BaseModel):
    order_id: int = Field(gt=0)
    customer: str = Field(min_length=2)
    product: str = Field(min_length=2)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class OrderOut(BaseModel):
    order_id: int
    customer: str
    product: str
    quantity: int
    unit_price: float
    total: float
    status: Literal["created", "paid", "cancelled"]
    created_at: datetime


def order_in_to_entity(order_in: OrderIn) -> Order:
    return Order(
        order_id=order_in.order_id,
        customer=order_in.customer,
        product=order_in.product,
        quantity=order_in.quantity,
        unit_price=order_in.unit_price,
    )


def entity_to_order_out(order: Order) -> OrderOut:
    return OrderOut(
        order_id=order.order_id,
        customer=order.customer,
        product=order.product,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total=order.total,
        status="created",
        created_at=datetime.now(),
    )


def print_serialized_order(order_out: OrderOut) -> None:
    data: dict[str, Any] = order_out.model_dump()
    print(data)


def main() -> None:
    entrada: OrderData = {
        "order_id": 1,
        "customer": "Ana López",
        "product": "Laptop",
        "quantity": 2,
        "unit_price": 12500.50,
    }

    order_in = OrderIn(**entrada)
    order_entity = order_in_to_entity(order_in)
    order_out = entity_to_order_out(order_entity)

    print("Entidad Order:")
    print(order_entity)

    print("\nOrderOut serializado:")
    print_serialized_order(order_out)

    print("\nOrderOut JSON:")
    print(order_out.model_dump_json(indent=2))

    print("\nComparación de órdenes por total:")
    order_2 = Order(
        order_id=2,
        customer="Luis Pérez",
        product="Monitor",
        quantity=1,
        unit_price=3000,
    )

    print(order_entity > order_2)


if __name__ == "__main__":
    main()
