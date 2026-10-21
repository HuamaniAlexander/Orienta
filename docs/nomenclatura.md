# Nomenclatura de ORIENTA

Las carpetas técnicas de arquitectura conservan su nombre en inglés. Los símbolos, funcionalidades y documentación propios usan español, sin tildes en identificadores. Se respeta la estructura existente `backend/app`; no se introduce un segundo árbol `backend/src`.

## Correspondencias principales

| Antes | Ahora |
| --- | --- |
| `Career`, `Source` | `Carrera`, `Fuente` |
| `Catalog`, `CompareCareers`, `AnalyzeComparison` | `Catalogo`, `CompararCarreras`, `AnalizarComparacion` |
| `CareerRepository` | `RepositorioCarreras` |
| `JsonCareerRepository`, `SqlCareerRepository` | `RepositorioCarrerasJson`, `RepositorioCarrerasSql` |
| `Settings` | `Configuracion` |
| `CareerCard.tsx`, `ComparePage.tsx` | `TarjetaCarrera.tsx`, `PaginaComparar.tsx` |
| `AnalysisPanel.tsx` | `PanelRecomendacionIA.tsx` |
| `application/useResource.ts` | `hooks/useRecurso.ts` |
| `domain/career.py` | `domain/carrera.py` |
| `application/compare.py` | `application/comparar_carreras.py` |
| `infrastructure/train_models.py` | `infrastructure/entrenar_modelos.py` |
| `institutions`, `imports` | `instituciones`, `importaciones` |
| `academic_offers`, `sources` | `ofertas_academicas`, `fuentes` |
| `name`, `monthly_cost_pen`, `duration_months` en PostgreSQL | `nombre`, `costo_mensual_soles`, `duracion_meses` |

Los módulos Python usan `snake_case`; los componentes e interfaces TypeScript, `PascalCase`; sus variables y funciones, `camelCase`. Los hooks mantienen el prefijo técnico `use`.

## Compatibilidad

- Las rutas `/api/carreras`, `/api/filtros`, `/api/comparaciones`, `/api/comparaciones/analisis` y `/api/salud` conservan su contrato. Las claves externas como `career_ids`, `name` y `monthly_cost_pen` permanecen estables.
- `backend/app/adapters/contratos.py` y los alias Pydantic separan nombres internos y externos. `frontend/src/adapters/contratosApi.ts` realiza la traducción en Fetch. No se distribuyen alias de transporte por el dominio.
- Las variables de entorno existentes, como `DATABASE_URL`, `DATA_MODE` y `CORS_ORIGINS`, siguen funcionando. Los nombres de scikit-learn, SQLAlchemy, FastAPI, React, HTML, pytest y Alembic permanecen intactos.
- Los comandos históricos `app.infrastructure.main:app`, `train_models`, `seed_catalog`, `import_excel` y `recommendation_training` delegan en los módulos canónicos en español. Los argumentos CLI anteriores siguen aceptándose como alias.
- `scripts/Iniciar-Orienta.ps1` es el inicio canónico; `Start-Orienta.ps1` conserva el comando anterior. Las migraciones históricas permanecen intactas; `0002_nomenclatura_espanol.py` renombra tablas y columnas sin eliminar registros y permite revertir los nombres.
- Los nombres y claves de los formatos JSON anteriores, los identificadores académicos y los predictores/etiquetas del modelo se conservan como contratos de datos. El catálogo y los artefactos se llaman ahora `catalogo.json`, `modelo.joblib` y `metricas.json`; sus contenidos se preservan.

## Verificación

La suite incluye una prueba de migración de ida y vuelta con registros existentes y una comparación completa de las respuestas de la API anteriores al cambio. El frontend verifica que las solicitudes conservan las claves originales. Además se ejecutan compilación, lint, pruebas de integración con PostgreSQL y entrenamiento reproducible en una salida temporal.
