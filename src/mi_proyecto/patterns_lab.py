from dataclasses import dataclass
from functools import wraps
from typing import Protocol


@dataclass
class Order:
    id: int
    customer: str
    subtotal: float


class PricingStrategy(Protocol):
    def calculate_total(self, order: Order) -> float: ...


class RegularPricing:
    def calculate_total(self, order: Order) -> float:
        return order.subtotal


class DiscountPricing:
    def __init__(self, discount_percent: float) -> None:
        self.discount_percent = discount_percent

    def calculate_total(self, order: Order) -> float:
        discount = order.subtotal * (self.discount_percent / 100)
        return order.subtotal - discount


class PremiumPricing:
    def calculate_total(self, order: Order) -> float:
        return order.subtotal * 0.90


class PricingService:
    def __init__(self, strategy: PricingStrategy) -> None:
        self.strategy = strategy

    def get_total(self, order: Order) -> float:
        return self.strategy.calculate_total(order)


def cache_result(function):
    cache = {}

    @wraps(function)
    def wrapper(*args):
        if args in cache:
            print("Resultado obtenido desde caché")
            return cache[args]

        result = function(*args)
        cache[args] = result
        return result

    return wrapper


@cache_result
def get_tax_rate(country: str) -> float:
    print("Consultando tasa externa...")
    rates = {
        "MX": 0.16,
        "US": 0.08,
        "ES": 0.21,
    }
    return rates.get(country, 0.0)


class ExternalPaymentProvider:
    def make_payment(self, amount: float) -> str:
        return f"Pago externo realizado por ${amount:.2f}"


class PaymentProcessor(Protocol):
    def pay(self, amount: float) -> str: ...


class PaymentAdapter:
    def __init__(self, provider: ExternalPaymentProvider) -> None:
        self.provider = provider

    def pay(self, amount: float) -> str:
        return self.provider.make_payment(amount)


def main() -> None:
    order = Order(id=1, customer="Ana López", subtotal=1000.0)

    regular_service = PricingService(RegularPricing())
    discount_service = PricingService(DiscountPricing(15))
    premium_service = PricingService(PremiumPricing())

    print("Strategy:")
    print(regular_service.get_total(order))
    print(discount_service.get_total(order))
    print(premium_service.get_total(order))

    print("\nDecorator caché:")
    print(get_tax_rate("MX"))
    print(get_tax_rate("MX"))

    print("\nAdapter:")
    external_provider = ExternalPaymentProvider()
    processor = PaymentAdapter(external_provider)
    print(processor.pay(850.0))


if __name__ == "__main__":
    main()
