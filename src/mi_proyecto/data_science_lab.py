from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "clientes.csv"
MODEL_PATH = BASE_DIR / "modelo_abandono.joblib"


def cargar_datos(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta)

    df = df.dropna()
    df = df.drop_duplicates()

    return df


def entrenar_modelo(df: pd.DataFrame) -> RandomForestClassifier:
    x = df[["edad", "ingresos", "compras_previas"]]
    y = df["abandono"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.3,
        random_state=42,
    )

    modelo = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )

    modelo.fit(x_train, y_train)

    predicciones = modelo.predict(x_test)

    print("Accuracy:", accuracy_score(y_test, predicciones))
    print("\nReporte de clasificación:")
    print(classification_report(y_test, predicciones))

    return modelo


def guardar_modelo(modelo: RandomForestClassifier, ruta: Path) -> None:
    joblib.dump(modelo, ruta)
    print(f"Modelo guardado en: {ruta}")


def probar_inferencia(ruta_modelo: Path) -> None:
    modelo = joblib.load(ruta_modelo)

    nuevo_cliente = pd.DataFrame(
        [
            {
                "edad": 27,
                "ingresos": 16000,
                "compras_previas": 2,
            }
        ]
    )

    prediccion = modelo.predict(nuevo_cliente)[0]

    resultado = "Abandona" if prediccion == 1 else "No abandona"

    print("\nInferencia:")
    print(nuevo_cliente)
    print(f"Predicción: {resultado}")


def main() -> None:
    df = cargar_datos(CSV_PATH)

    print("Datos cargados:")
    print(df.head())

    modelo = entrenar_modelo(df)
    guardar_modelo(modelo, MODEL_PATH)
    probar_inferencia(MODEL_PATH)


if __name__ == "__main__":
    main()
