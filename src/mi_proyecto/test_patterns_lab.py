from mi_proyecto.patterns_lab import (DiscountPricing, ExternalPaymentProvider,
                                      Order, PaymentAdapter, PremiumPricing,
                                      PricingService, RegularPricing,
                                      get_tax_rate)


def test_regular_pricing_strategy() -> None:
    order = Order(id=1, customer="Ana López", subtotal=1000.0)
    service = PricingService(RegularPricing())

    assert service.get_total(order) == 1000.0


def test_discount_pricing_strategy() -> None:
    order = Order(id=1, customer="Ana López", subtotal=1000.0)
    service = PricingService(DiscountPricing(15))

    assert service.get_total(order) == 850.0


def test_premium_pricing_strategy() -> None:
    order = Order(id=1, customer="Ana López", subtotal=1000.0)
    service = PricingService(PremiumPricing())

    assert service.get_total(order) == 900.0


def test_cache_decorator() -> None:
    first_result = get_tax_rate("MX")
    second_result = get_tax_rate("MX")

    assert first_result == 0.16
    assert second_result == 0.16


def test_payment_adapter() -> None:
    provider = ExternalPaymentProvider()
    adapter = PaymentAdapter(provider)

    assert adapter.pay(850.0) == "Pago externo realizado por $850.00"
