from mi_proyecto.clean.application.create_order import CreateOrderOutput


class OrderPresenter:
    def present(self, output: CreateOrderOutput) -> dict[str, object]:
        return {
            "id": output.id,
            "customer": output.customer,
            "total": output.total,
            "message": "Orden creada correctamente",
        }
