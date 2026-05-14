from mi_proyecto.hexagonal.application.create_order import (CreateOrderCommand,
                                                            CreateOrderUseCase,
                                                            OrderItemDTO)
from mi_proyecto.hexagonal.infrastructure.http_notifier import FakeHttpNotifier
from mi_proyecto.hexagonal.infrastructure.memory_repository import \
    InMemoryOrderRepository


def main() -> None:
    repository = InMemoryOrderRepository()
    notifier = FakeHttpNotifier()

    use_case = CreateOrderUseCase(repository, notifier)

    command = CreateOrderCommand(
        customer="Ana López",
        items=[
            OrderItemDTO(product="Laptop", quantity=1, unit_price=12500.5),
            OrderItemDTO(product="Mouse", quantity=2, unit_price=350.0),
        ],
    )

    order = use_case.execute(command)

    print("Orden creada correctamente")
    print(f"ID: {order.id}")
    print(f"Cliente: {order.customer}")
    print(f"Total: {order.total}")
    print(f"Notificaciones: {notifier.sent_notifications}")


if __name__ == "__main__":
    main()
