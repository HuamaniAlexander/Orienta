NAMES = {
    "UTP": "Universidad Tecnológica del Perú",
    "UNMSM": "Universidad Nacional Mayor de San Marcos",
    "UNI": "Universidad Nacional de Ingeniería",
    "PUCP": "Pontificia Universidad Católica del Perú",
    "UPC": "Universidad Peruana de Ciencias Aplicadas",
}


def career_label(career):
    return f"{career.name} · {NAMES.get(career.institution, career.institution)}"
