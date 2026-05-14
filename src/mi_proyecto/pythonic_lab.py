import random
import time
from contextlib import contextmanager
from functools import wraps


def retry(max_intentos=3, backoff=1):
    def decorador(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            intento = 1

            while intento <= max_intentos:
                try:
                    return funcion(*args, **kwargs)
                except Exception as error:
                    print(f"Intento {intento} falló: {error}")

                    if intento == max_intentos:
                        print("Se agotaron los intentos.")
                        raise

                    espera = backoff * intento
                    print(f"Reintentando en {espera} segundos...")
                    time.sleep(espera)
                    intento += 1

        return wrapper

    return decorador


def generar_lotes(datos, tamano_lote):
    for indice in range(0, len(datos), tamano_lote):
        yield datos[indice : indice + tamano_lote]


@contextmanager
def medir_tiempo(nombre_proceso):
    inicio = time.time()
    print(f"Iniciando: {nombre_proceso}")

    try:
        yield
    finally:
        fin = time.time()
        duracion = fin - inicio
        print(f"Finalizó: {nombre_proceso}")
        print(f"Tiempo total: {duracion:.4f} segundos")


@retry(max_intentos=3, backoff=1)
def consumir_servicio():
    if random.choice([True, False]):
        raise ConnectionError("Error temporal de conexión")

    return "Servicio consumido correctamente"


def main():
    datos = list(range(1, 21))

    with medir_tiempo("Procesamiento por lotes"):
        for lote in generar_lotes(datos, 5):
            print(f"Lote procesado: {lote}")

    print("\nProbando decorador de reintentos:")

    try:
        resultado = consumir_servicio()
        print(resultado)
    except ConnectionError:
        print("No fue posible consumir el servicio.")


if __name__ == "__main__":
    main()
