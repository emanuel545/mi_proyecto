import time
from pathlib import Path

import httpx

BASE_DIR = Path(__file__).resolve().parents[2]
DOWNLOAD_PATH = BASE_DIR / "descarga.json"


def get_with_retries(
    url: str,
    max_retries: int = 3,
    backoff: float = 1.5,
    timeout: float = 5.0,
) -> dict:
    for attempt in range(1, max_retries + 1):
        try:
            with httpx.Client(timeout=timeout, http2=True) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            print(f"Intento {attempt}: timeout al conectar con la API")

        except httpx.HTTPStatusError as error:
            print(f"Intento {attempt}: error HTTP {error.response.status_code}")

        except httpx.RequestError as error:
            print(f"Intento {attempt}: error de conexión: {error}")

        if attempt < max_retries:
            wait_time = backoff * attempt
            print(f"Reintentando en {wait_time:.1f} segundos...")
            time.sleep(wait_time)

    raise RuntimeError("No fue posible consumir la API después de varios intentos")


def download_streaming(
    url: str,
    output_path: Path,
    timeout: float = 10.0,
) -> None:
    with httpx.Client(timeout=timeout, http2=True) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()

            with output_path.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)

    print(f"Archivo descargado correctamente en: {output_path}")


def main() -> None:
    api_url = "https://jsonplaceholder.typicode.com/posts/1"
    download_url = "https://jsonplaceholder.typicode.com/posts"

    print("Consumiendo API con reintentos y timeout...")
    data = get_with_retries(api_url)

    print("Respuesta:")
    print(data)

    print("\nDescargando respuesta por streaming...")
    download_streaming(download_url, DOWNLOAD_PATH)


if __name__ == "__main__":
    main()
