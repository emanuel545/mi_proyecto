import pytest
from hypothesis import given
from hypothesis import strategies as st

from mi_proyecto.order_service import calculate_total


@pytest.mark.parametrize(
    ("quantity", "unit_price", "discount_percent", "expected"),
    [
        (2, 100.0, 0.0, 200.0),
        (2, 100.0, 10.0, 180.0),
        (1, 500.0, 50.0, 250.0),
        (3, 200.0, 100.0, 0.0),
    ],
)
def test_calculate_total_with_valid_discount(
    quantity: int,
    unit_price: float,
    discount_percent: float,
    expected: float,
) -> None:
    result = calculate_total(quantity, unit_price, discount_percent)

    assert result == expected


@pytest.mark.parametrize(
    ("quantity", "unit_price", "discount_percent"),
    [
        (0, 100.0, 10.0),
        (-1, 100.0, 10.0),
        (1, 0.0, 10.0),
        (1, -100.0, 10.0),
        (1, 100.0, -5.0),
        (1, 100.0, 101.0),
    ],
)
def test_calculate_total_with_invalid_values(
    quantity: int,
    unit_price: float,
    discount_percent: float,
) -> None:
    with pytest.raises(ValueError):
        calculate_total(quantity, unit_price, discount_percent)


@given(
    quantity=st.integers(min_value=1, max_value=1000),
    unit_price=st.floats(min_value=0.01, max_value=100000, allow_nan=False),
    discount_percent=st.floats(min_value=0, max_value=100, allow_nan=False),
)
def test_total_is_never_negative(
    quantity: int,
    unit_price: float,
    discount_percent: float,
) -> None:
    total = calculate_total(quantity, unit_price, discount_percent)

    assert total >= 0


@given(
    quantity=st.integers(min_value=1, max_value=1000),
    unit_price=st.floats(min_value=0.01, max_value=100000, allow_nan=False),
)
def test_total_without_discount_equals_subtotal(
    quantity: int,
    unit_price: float,
) -> None:
    total = calculate_total(quantity, unit_price, 0)

    assert total == quantity * unit_price
