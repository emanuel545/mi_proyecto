import pytest

from mi_proyecto.hexagonal.application.create_order import (CreateOrderCommand,
                                                            CreateOrderUseCase,
                                                            OrderItemDTO)
from mi_proyecto.hexagonal.domain.order import Order, OrderItem
from mi_proyecto.hexagonal.infrastructure.http_notifier import FakeHttpNotifier
from mi_proyecto.hexagonal.infrastructure.memory_repository import \
    InMemoryOrderRepository
from mi_proyecto.hexagonal.infrastructure.sqlalchemy_repository import (
    SQLAlchemyOrderRepository, create_sqlite_memory_session)


@pytest.fixture
def sample_order() -> Order:
    return Order(
        customer="Ana López",
        items=[
            OrderItem(product="Laptop", quantity=1, unit_price=12500.5),
            OrderItem(product="Mouse", quantity=2, unit_price=350.0),
        ],
    )


@pytest.mark.parametrize(
    "repository",
    [
        InMemoryOrderRepository(),
        SQLAlchemyOrderRepository(create_sqlite_memory_session()),
    ],
)
def test_repository_contract_save_and_get(repository, sample_order: Order) -> None:
    repository.save(sample_order)

    saved_order = repository.get_by_id(sample_order.id)

    assert saved_order is not None
    assert saved_order.id == sample_order.id
    assert saved_order.customer == sample_order.customer
    assert saved_order.total == sample_order.total


def test_create_order_use_case_with_memory_adapter() -> None:
    repository = InMemoryOrderRepository()
    notifier = FakeHttpNotifier()
    use_case = CreateOrderUseCase(repository, notifier)

    command = CreateOrderCommand(
        customer="Ana López",
        items=[
            OrderItemDTO(product="Laptop", quantity=1, unit_price=12500.5),
        ],
    )

    order = use_case.execute(command)
    saved_order = repository.get_by_id(order.id)

    if saved_order is None:
        raise ValueError("Order no encontrada")

    assert saved_order.total == 12500.5
    assert len(notifier.sent_notifications) == 1


def test_create_order_invalid_empty_items() -> None:
    repository = InMemoryOrderRepository()
    notifier = FakeHttpNotifier()
    use_case = CreateOrderUseCase(repository, notifier)

    command = CreateOrderCommand(customer="Ana López", items=[])

    with pytest.raises(ValueError):
        use_case.execute(command)
