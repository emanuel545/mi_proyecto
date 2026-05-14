from mi_proyecto.clean.application.create_order import (CreateOrderInput,
                                                        CreateOrderUseCase,
                                                        OrderItemInput)
from mi_proyecto.clean.infrastructure.memory import (InMemoryEventPublisher,
                                                     InMemoryUnitOfWork)
from mi_proyecto.clean.presentation.presenter import OrderPresenter


def main() -> None:
    uow = InMemoryUnitOfWork()
    publisher = InMemoryEventPublisher()
    presenter = OrderPresenter()

    use_case = CreateOrderUseCase(uow, publisher)

    input_data = CreateOrderInput(
        customer="Ana López",
        items=[
            OrderItemInput(product="Laptop", quantity=1, unit_price=12500.5),
            OrderItemInput(product="Mouse", quantity=2, unit_price=350.0),
        ],
    )

    output = use_case.execute(input_data)
    response = presenter.present(output)

    print(response)
    print(f"Commit ejecutado: {uow.committed}")
    print(f"Eventos publicados: {len(publisher.published_events)}")


if __name__ == "__main__":
    main()
