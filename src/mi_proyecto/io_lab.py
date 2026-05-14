import csv
import json
import logging
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "ventas.csv"
OUTPUT_PATH = BASE_DIR / "metricas_ventas.json"
LOG_PATH = BASE_DIR / "app.log"


logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def leer_csv(ruta: Path) -> list[dict[str, str]]:
    logging.info("Iniciando lectura del archivo CSV")

    if not ruta.exists():
        logging.error("El archivo CSV no existe: %s", ruta)
        return []

    with ruta.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        datos = list(lector)

    logging.info("Se leyeron %s registros del CSV", len(datos))
    return datos


def calcular_metricas(datos: list[dict[str, str]]) -> dict[str, object]:
    logging.info("Calculando métricas de ventas")

    total_ventas = 0.0
    total_productos = 0
    ventas_por_categoria: dict[str, float] = {}

    for fila in datos:
        try:
            categoria = fila["categoria"]
            cantidad = int(fila["cantidad"])
            precio = float(fila["precio_unitario"])
            subtotal = cantidad * precio

            total_ventas += subtotal
            total_productos += cantidad
            ventas_por_categoria[categoria] = (
                ventas_por_categoria.get(categoria, 0.0) + subtotal
            )

        except KeyError as error:
            logging.warning("Columna faltante en CSV: %s", error)
        except ValueError as error:
            logging.warning("Dato numérico inválido: %s", error)

    return {
        "fecha_generacion": datetime.now().isoformat(),
        "total_ventas": total_ventas,
        "total_productos": total_productos,
        "ventas_por_categoria": ventas_por_categoria,
    }


def exportar_json(datos: dict[str, object], ruta: Path) -> None:
    logging.info("Exportando métricas a JSON")

    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)

    logging.info("Archivo JSON generado correctamente: %s", ruta)


def main() -> None:
    logging.info("Inicio del proceso de ingesta")

    datos = leer_csv(CSV_PATH)

    if not datos:
        logging.error("No hay datos para procesar")
        return

    metricas = calcular_metricas(datos)
    exportar_json(metricas, OUTPUT_PATH)

    print("Métricas generadas correctamente")
    print(f"Archivo JSON: {OUTPUT_PATH}")
    print(f"Archivo log: {LOG_PATH}")

    logging.info("Proceso finalizado correctamente")


if __name__ == "__main__":
    main()
