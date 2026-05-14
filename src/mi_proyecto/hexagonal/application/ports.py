from typing import Protocol

from mi_proyecto.hexagonal.domain.order import Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...

    def get_by_id(self, order_id: str) -> Order | None: ...


class NotificationPort(Protocol):
    def notify_order_created(self, order: Order) -> None: ...
