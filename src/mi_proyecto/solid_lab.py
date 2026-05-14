from typing import Protocol


# =========================
# ENTIDAD (SRP)
# =========================
class Order:
    def __init__(self, id: int, total: float):
        self.id = id
        self.total = total


# =========================
# PUERTO (DIP)
# =========================
class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...
    def get(self, order_id: int) -> Order | None: ...


# =========================
# IMPLEMENTACIÓN EN MEMORIA
# =========================
class InMemoryOrderRepository:
    def __init__(self):
        self.storage: dict[int, Order] = {}

    def save(self, order: Order) -> None:
        self.storage[order.id] = order

    def get(self, order_id: int) -> Order | None:
        return self.storage.get(order_id)


# =========================
# IMPLEMENTACIÓN SIMULADA SQL
# =========================
class SQLOrderRepository:
    def __init__(self):
        self.storage: dict[int, Order] = {}

    def save(self, order: Order) -> None:
        print("Guardando en base de datos...")
        self.storage[order.id] = order

    def get(self, order_id: int) -> Order | None:
        return self.storage.get(order_id)


# =========================
# SERVICIO (DIP + SRP)
# =========================
class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def create_order(self, order_id: int, total: float) -> None:
        order = Order(order_id, total)
        self.repo.save(order)

    def get_order(self, order_id: int) -> Order | None:
        return self.repo.get(order_id)


# =========================
# LSP DEMO
# =========================
def demo(repository: OrderRepository) -> None:
    service = OrderService(repository)

    service.create_order(1, 100.0)
    order = service.get_order(1)

    if order is None:
        raise ValueError("Order no encontrada")

    print(f"Order encontrada: {order.id}, total: {order.total}")


def main() -> None:
    print("Usando repositorio en memoria:")
    demo(InMemoryOrderRepository())

    print("\nUsando repositorio SQL:")
    demo(SQLOrderRepository())


if __name__ == "__main__":
    main()
