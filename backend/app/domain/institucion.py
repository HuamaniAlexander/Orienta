NOMBRES = {
    "UTP": "Universidad Tecnológica del Perú",
    "UNMSM": "Universidad Nacional Mayor de San Marcos",
    "UNI": "Universidad Nacional de Ingeniería",
    "PUCP": "Pontificia Universidad Católica del Perú",
    "UPC": "Universidad Peruana de Ciencias Aplicadas",
}


def etiqueta_carrera(carrera):
    return f"{carrera.nombre} · {NOMBRES.get(carrera.institucion, carrera.institucion)}"
