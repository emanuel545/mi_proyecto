from mi_proyecto.clean.application.ports import OrderRepository
from mi_proyecto.clean.domain.order import DomainEvent, Order


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self.orders: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self.orders[order.id] = order

    def get_by_id(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.orders = InMemoryOrderRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
