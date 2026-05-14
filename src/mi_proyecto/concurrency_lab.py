import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

import httpx

URLS = [
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/posts/3",
    "https://jsonplaceholder.typicode.com/posts/4",
    "https://jsonplaceholder.typicode.com/posts/5",
]


def fetch_sync(url: str) -> dict:
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def run_sync_fetcher() -> list[dict]:
    results = []

    for url in URLS:
        data = fetch_sync(url)
        results.append(data)

    return results


async def fetch_async(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    async with semaphore:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def run_async_fetcher() -> list[dict]:
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [fetch_async(client, url, semaphore) for url in URLS]

        return await asyncio.gather(*tasks)


def cpu_bound_task(number: int) -> int:
    total = 0

    for value in range(number):
        total += value * value

    return total


def run_cpu_bound_tasks() -> list[int]:
    numbers = [5_000_000, 5_000_000, 5_000_000, 5_000_000]

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(cpu_bound_task, numbers))

    return results


def measure_time(label: str, function):
    start = time.perf_counter()
    result = function()
    end = time.perf_counter()

    print(f"{label}: {end - start:.4f} segundos")

    return result


async def main() -> None:
    print("Fetcher síncrono:")
    sync_results = measure_time("Tiempo sync", run_sync_fetcher)
    print(f"Resultados sync: {len(sync_results)}")

    print("\nFetcher asíncrono:")
    start = time.perf_counter()
    async_results = await run_async_fetcher()
    end = time.perf_counter()

    print(f"Tiempo async: {end - start:.4f} segundos")
    print(f"Resultados async: {len(async_results)}")

    print("\nCPU-bound con ProcessPoolExecutor:")
    cpu_results = measure_time("Tiempo multiprocessing", run_cpu_bound_tasks)
    print(f"Resultados CPU: {len(cpu_results)}")


if __name__ == "__main__":
    asyncio.run(main())
