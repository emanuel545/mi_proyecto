from mi_proyecto.hexagonal.domain.order import Order


class FakeHttpNotifier:
    def __init__(self) -> None:
        self.sent_notifications: list[str] = []

    def notify_order_created(self, order: Order) -> None:
        message = f"Orden creada: {order.id} | Total: {order.total:.2f}"
        self.sent_notifications.append(message)
