import os
from typing import Any

import httpx
import typer

app = typer.Typer(help="CLI para gestionar órdenes consumiendo la API FastAPI.")

API_URL = os.getenv("ORDERS_API_URL", "http://127.0.0.1:8000/api/v1")

TOKEN: str | None = None


def login() -> str:
    response = httpx.post(
        f"{API_URL}/login",
        data={"username": "admin", "password": "1234"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_headers() -> dict[str, str]:
    token = login()
    return {"Authorization": f"Bearer {token}"}


@app.command()
def listar() -> None:
    """Lista las órdenes existentes."""
    response = httpx.get(
        f"{API_URL}/orders",
        headers=get_headers(),
        timeout=10,
    )
    response.raise_for_status()

    orders: list[dict[str, Any]] = response.json()

    if not orders:
        typer.echo("No hay órdenes registradas.")
        return

    for order in orders:
        typer.echo(
            f"ID: {order['id']} | Cliente: {order['customer']} | "
            f"Producto: {order['product']} | Total: ${order['total']}"
        )


@app.command()
def crear(
    customer: str = typer.Option(..., help="Nombre del cliente"),
    product: str = typer.Option(..., help="Producto"),
    quantity: int = typer.Option(..., help="Cantidad"),
    unit_price: float = typer.Option(..., help="Precio unitario"),
) -> None:
    """Crea una nueva orden."""
    payload = {
        "customer": customer,
        "product": product,
        "quantity": quantity,
        "unit_price": unit_price,
    }

    response = httpx.post(
        f"{API_URL}/orders",
        headers=get_headers(),
        json=payload,
        timeout=10,
    )
    response.raise_for_status()

    order = response.json()
    typer.echo(f"Orden creada correctamente. ID: {order['id']}")


@app.command()
def borrar(order_id: int) -> None:
    """Elimina una orden por ID."""
    response = httpx.delete(
        f"{API_URL}/orders/{order_id}",
        headers=get_headers(),
        timeout=10,
    )
    response.raise_for_status()

    typer.echo("Orden eliminada correctamente.")


if __name__ == "__main__":
    app()
