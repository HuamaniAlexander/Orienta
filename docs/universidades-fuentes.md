> Registro del catálogo histórico de 35 ofertas. El catálogo vigente contiene 405 ofertas: [integración completa](catalogo-completo.md).

# Catálogo ampliado e identidad institucional

Revisión del 20/10/2026. Se conservan las 19 ofertas originales y se incorporan 16: cuatro de la Pontificia Universidad Católica del Perú, ocho de la Universidad Nacional de Ingeniería y cuatro de la Universidad Peruana de Ciencias Aplicadas. Total: 35 ofertas y cinco universidades; dos públicas y tres privadas.

Cada nueva ficha registra su URL oficial y estado por campo en `backend/data/catalogo.json`. La duración de diez semestres se expresa como 60 meses académicos; no garantiza una fecha de egreso. No se deducen gratuidad, pensiones, requisitos de ingreso ni sedes a partir del carácter público o privado de la institución. Los campos no corroborados quedan nulos. Los nombres de áreas en `areas.json` son etiquetas disciplinares del equipo para el experimento, no una clasificación institucional publicada.

Fuentes principales:

- https://www.pucp.edu.pe/carrera/ingenieria-informatica/
- https://www.pucp.edu.pe/carrera/ingenieria-civil/
- https://www.pucp.edu.pe/carrera/ingenieria-industrial/
- https://www.pucp.edu.pe/carrera/economia/
- https://portal.uni.edu.pe/index.php/45-pregrado/carreras
- https://pregrado.upc.edu.pe/
- https://www.upc.edu.pe/epe/carreras/ingenieria-de-software

Los logos se obtuvieron de las webs oficiales. `frontend/public/instituciones/fuentes.json` registra los archivos originales; el logo UTP se extrajo del SVG de su encabezado y UPC usa el símbolo oficial publicado como favicon SVG. Se conservan las marcas de sus titulares, se usan para identificar instituciones y no se afirma afiliación ni licencia de redistribución. Los archivos son locales para evitar solicitudes externas durante la navegación.

Los códigos institucionales se mantienen en persistencia para conservar identidades y compatibilidad del importador. La interfaz muestra logos y nombres completos. Las explicaciones y las etiquetas accesibles identifican carrera y universidad en lugar de letras.
