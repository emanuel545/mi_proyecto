from fastapi.testclient import TestClient

from mi_proyecto.api_lab import Base, app, engine

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_token() -> str:
    response = client.post(
        "/api/v1/login",
        data={"username": "admin", "password": "1234"},
    )
    return response.json()["access_token"]


def test_login_success() -> None:
    response = client.post(
        "/api/v1/login",
        data={"username": "admin", "password": "1234"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_order() -> None:
    token = get_token()

    response = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer": "Ana López",
            "product": "Laptop",
            "quantity": 2,
            "unit_price": 12500.5,
        },
    )

    assert response.status_code == 201
    assert response.json()["total"] == 25001.0


def test_create_order_without_token() -> None:
    response = client.post(
        "/api/v1/orders",
        json={
            "customer": "Ana López",
            "product": "Laptop",
            "quantity": 2,
            "unit_price": 12500.5,
        },
    )

    assert response.status_code == 401
