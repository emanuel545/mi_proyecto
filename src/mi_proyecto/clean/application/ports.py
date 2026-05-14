from typing import Any, Protocol

from mi_proyecto.clean.domain.order import DomainEvent, Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...

    def get_by_id(self, order_id: str) -> Order | None: ...


class UnitOfWork(Protocol):
    orders: Any

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
