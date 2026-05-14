import json
import re


def leer_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Error: archivo no encontrado")
    except json.JSONDecodeError:
        print("Error: formato JSON inválido")
    return []


def validar_correo(correo):
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, correo)


def clasificar(usuario):
    match usuario:
        case {"edad": edad} if edad >= 18:
            return "Mayor de edad"
        case {"edad": edad} if edad < 18:
            return "Menor de edad"
        case _:
            return "Sin datos"


def procesar(datos):
    resultado = []

    for usuario in datos:
        if usuario.get("activo") and validar_correo(usuario.get("correo", "")):
            usuario["clasificacion"] = clasificar(usuario)
            resultado.append(usuario)

    return resultado


def main():
    datos = leer_json("datos.json")
    usuarios = procesar(datos)

    print("Usuarios válidos:")

    for u in usuarios:
        print(f"{u['nombre']} - {u['correo']} - {u['clasificacion']}")


if __name__ == "__main__":
    main()
