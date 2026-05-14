import pytest

from mi_proyecto.clean.application.create_order import (CreateOrderInput,
                                                        CreateOrderUseCase,
                                                        OrderItemInput)
from mi_proyecto.clean.domain.order import OrderCreated
from mi_proyecto.clean.infrastructure.memory import (InMemoryEventPublisher,
                                                     InMemoryUnitOfWork)
from mi_proyecto.clean.presentation.presenter import OrderPresenter


def test_create_order_use_case_commits_and_publishes_event() -> None:
    uow = InMemoryUnitOfWork()
    publisher = InMemoryEventPublisher()
    use_case = CreateOrderUseCase(uow, publisher)

    input_data = CreateOrderInput(
        customer="Ana López",
        items=[
            OrderItemInput(product="Laptop", quantity=1, unit_price=12500.5),
        ],
    )

    output = use_case.execute(input_data)

    saved_order = uow.orders.get_by_id(output.id)

    assert saved_order is not None
    assert output.total == 12500.5
    assert uow.committed is True
    assert len(publisher.published_events) == 1
    assert isinstance(publisher.published_events[0], OrderCreated)


def test_create_order_rollback_when_invalid_data() -> None:
    uow = InMemoryUnitOfWork()
    publisher = InMemoryEventPublisher()
    use_case = CreateOrderUseCase(uow, publisher)

    input_data = CreateOrderInput(customer="", items=[])

    with pytest.raises(ValueError):
        use_case.execute(input_data)

    assert uow.rolled_back is True
    assert len(publisher.published_events) == 0


def test_presenter_formats_response() -> None:
    uow = InMemoryUnitOfWork()
    publisher = InMemoryEventPublisher()
    use_case = CreateOrderUseCase(uow, publisher)
    presenter = OrderPresenter()

    input_data = CreateOrderInput(
        customer="Ana López",
        items=[
            OrderItemInput(product="Mouse", quantity=2, unit_price=350.0),
        ],
    )

    output = use_case.execute(input_data)
    response = presenter.present(output)

    assert response["customer"] == "Ana López"
    assert response["total"] == 700.0
    assert response["message"] == "Orden creada correctamente"
