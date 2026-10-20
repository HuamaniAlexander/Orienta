# Trazabilidad de la entrega integrada

Las pruebas se ejecutaron sobre la entrega del 20/10/2026. No sustituyen la revisión
académica del equipo ni las sesiones de usabilidad con personas reales.

| Tareas / historia | Criterio Given–When–Then | Evidencia automatizada |
| --- | --- | --- |
| ORI-013 a 018 / datos | Dado un libro inválido o duplicado, al importar, se rechaza sin escritura parcial; repetir uno válido no duplica ofertas. | `backend/tests/test_data.py`, `conftest.py` |
| ORI-024/031 a 033 / HU01 | Dadas ofertas activas, al consultar, se pagina el catálogo; al fallar la conexión se muestra reintento; sin ofertas se muestra vacío. | `test_api.py`, `test_data.py`, `frontend/src/test/catalog.test.tsx` |
| ORI-034 a 038 / HU02 | Dados nombre y filtros, al combinarlos, se conservan en URL y se descartan respuestas obsoletas; sin coincidencias se permite limpiar. | `test_api.py`, `test_data.py`, `catalog.test.tsx` |
| ORI-039 a 043 / HU03 | Dada una ficha, al abrirla, se muestran seis criterios y fuentes; faltantes son distintos de cero; una oferta inexistente devuelve 404. | `frontend/src/test/detail.test.tsx`, `test_api.py` |
| ORI-026/044 a 050 / HU04 | Dadas dos alternativas distintas, al comparar, se conservan seis criterios; una selección duplicada/incompleta se rechaza; sustituir conserva la otra. | `backend/tests/test_comparison.py`, `frontend/src/test/comparison.test.tsx` |
| ORI-051 a 054 / HU05 parcial | Dada pantalla reducida, se apilan tarjetas y criterios; etiquetas, foco y controles siguen disponibles. | Revisión de navegador en pantalla estrecha y escritorio; pruebas de controles accesibles React |
| ORI-056 a 060 / HU-IA01 | Dados grupos de carrera, al entrenar/evaluar, ningún grupo se comparte entre entrenamiento y validación/prueba; se reproducen métricas del artefacto. | `backend/tests/test_ml.py`, `models/metrics.json` |
| ORI-064/065 / HU-IA01 | Dado un modelo disponible, al analizar, se separa predicción de catálogo; si falla IA se conserva la tabla y se permite reintentar. | `backend/tests/test_ml.py`, `frontend/src/test/analysis.test.tsx` |

## Mejoras registradas

- Se corrigió la separación interna por grupos antes de construir pares, evitando
  contaminación también en la selección del clasificador.
- Se corrigió el uso de una opción de Testing Library incompatible con los tipos de build.
- Se conserva el modo de sustitución al limpiar filtros y se maneja paginación fuera de rango.
- Se añadió una carga idempotente del catálogo versionado para no depender de Descargas.
- Se mantiene la comparación ante errores del análisis y se detectan modelos desactualizados.
- Se conserva el costo explícito cero y las advertencias de estimaciones del archivo fuente.

## Pendiente de evidencia externa

ORI-071: protocolo/sesiones con tres usuarios representativos reales. No se simulan participantes.
ORI-019: verificación vigente de cada información institucional y ampliación editorial del catálogo.
ORI-011/078: matrices ponderadas validadas por el equipo. No se inventan puntuaciones.
ORI-061/062: proveedor de explicación generativa sigue sin decidirse; el sistema identifica
el clasificador entrenado y las orientaciones deterministas, sin simular un LLM.
ORI-055/070: no se certifica una matriz exhaustiva de dispositivos, navegadores ni tecnologías de asistencia.
ORI-079: release y despliegue de producción quedan fuera de esta entrega.

Los PR correspondientes y los resultados de CI documentan los commits remotos. `main`
no se modifica. Las capturas de `docs/evidencias` proceden de la aplicación conectada a PostgreSQL.
