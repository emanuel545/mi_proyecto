def calculate_total(
    quantity: int,
    unit_price: float,
    discount_percent: float = 0.0,
) -> float:
    if quantity <= 0:
        raise ValueError("La cantidad debe ser mayor a cero")

    if unit_price <= 0:
        raise ValueError("El precio unitario debe ser mayor a cero")

    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("El descuento debe estar entre 0 y 100")

    subtotal = quantity * unit_price
    discount_amount = subtotal * (discount_percent / 100)
    return subtotal - discount_amount
