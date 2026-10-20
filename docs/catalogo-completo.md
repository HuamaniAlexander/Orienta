# Catálogo completo y pantallas de referencia

El archivo entregado `orienta_lima_norte_catalogo_completo_2026.json` se conserva íntegro en `backend/data/catalogo_lima_norte_2026.json`, con fecha de referencia 20/10/2026: **25 instituciones (14 universidades y 11 institutos), 196 carreras distintas y 405 ofertas**. Una oferta corresponde a una carrera en una institución y, cuando aplica, una sede. Por eso las carreras pueden aparecer en varias tarjetas.

## Importación y persistencia

Desde `backend`, después de configurar PostgreSQL y ejecutar `python -m alembic upgrade head`, ejecutar:

```powershell
python -m app.infrastructure.cargar_catalogo
```

El importador valida las relaciones con instituciones y carreras, identificadores e identidades duplicadas antes de escribir; conserva los identificadores originales, de hasta 89 caracteres, y el contenido completo de cada programa en `ofertas_academicas.detalles`. El JSON versionado mantiene además las entidades, perfiles y metadatos originales. No se requieren archivos de Downloads para reproducirlo.

La transacción se identifica por SHA-256 y es idempotente. Las ofertas del catálogo anterior dejan de publicarse, conservándose en la base como inactivas. Las API existentes mantienen rutas y campos; `detalles`, filtros adicionales y `/api/instituciones` son ampliaciones. Los identificadores históricos retirados devuelven el estado habitual de oferta no disponible.

La migración `0003` amplía identificadores en ofertas y fuentes, añade búsqueda normalizada y detalles. Una reversión que pudiera truncar identificadores largos se detiene explícitamente: respaldar y exportar antes de revertir. No se reescribieron migraciones aplicadas.

## Procedencia

El JSON combina catálogos citados con estimaciones. Los importes de matrícula, pensiones, inversión, ingresos y demanda **no son cifras oficiales certificadas**. Algunas modalidades, duraciones, títulos, requisitos y asignaciones a sedes también son modelados. Las fichas y el análisis conservan las fuentes y condiciones; no se convierten en datos verificados al importarlos.

El clasificador histórico de áreas cubre 35 ofertas. Para las nuevas se omite su inferencia y cualquier porcentaje de evaluación inexistente, conservando las explicaciones estructuradas de los seis criterios. El recomendador aprendido continúa sujeto al protocolo de revisión humana y evaluación independiente; este cambio no demuestra una exactitud superior al 90%.

## Interfaz y comprobaciones

Explorar adopta el banner con fotografía, búsqueda coral, filtros laterales, selección resaltada y tarjetas con portadas de las referencias. Comparar incorpora dos fichas, panel lateral de orientación, pestañas y tabla detallada. Instituciones permite consultar las 25 y acceder a sus ofertas. Los filtros se aplican a todo el catálogo antes de paginar.

Las portadas son ilustraciones fotográficas generadas para la interfaz; no representan campus ni alumnos de las instituciones. Las marcas descargadas se documentan en `frontend/public/instituciones/catalogo-fuentes.json`; las que no están disponibles usan un símbolo institucional común, sin inventar un logotipo.

Las pruebas contrastan los 405 identificadores recibidos con el JSON, las 25 instituciones, las 196 carreras, la repetición de importación, filtros y búsqueda, comparaciones con identificadores largos y el análisis de los seis criterios. Las pruebas de compatibilidad conservan el catálogo histórico como conjunto de referencia explícito.
