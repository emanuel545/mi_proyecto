import pytest

from mi_proyecto.solid_lab import (InMemoryOrderRepository, OrderService,
                                   SQLOrderRepository)


@pytest.mark.parametrize(
    "repo",
    [
        InMemoryOrderRepository(),
        SQLOrderRepository(),
    ],
)
def test_lsp(repo) -> None:
    service = OrderService(repo)

    service.create_order(1, 100.0)
    order = service.get_order(1)

    assert order is not None
    assert order.total == 100.0
