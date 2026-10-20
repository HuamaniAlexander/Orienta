# ORIENTA — MVP 1

Plataforma de orientación académica para jóvenes de Lima Norte. Permite explorar carreras, buscar y filtrar ofertas, consultar fichas con fuentes y comparar exactamente dos opciones sin crear una cuenta.

El catálogo entregado contiene **405 ofertas académicas, 196 carreras distintas y 25 instituciones** (14 universidades y 11 institutos). Compara duración, modalidad, ubicación, costo mensual, requisitos y campo laboral, con nombres completos, fuentes y marcas institucionales disponibles. Incluye filtros por gestión, distrito, área e institución y la página de instituciones.

## Stack tecnológico

| Capa | Tecnologías |
| --- | --- |
| Interfaz | React, TypeScript, Vite, Tailwind CSS, React Router |
| API | Python 3.12, FastAPI, Pydantic |
| Persistencia | PostgreSQL, SQLAlchemy, Alembic |
| Alojamiento de base de datos | InsForge, exclusivamente para PostgreSQL |
| Machine Learning | scikit-learn, pandas, NumPy, joblib |
| Pruebas | pytest, Vitest, Testing Library; GitHub Actions |

## Arquitectura y estructura

Arquitectura hexagonal: **dominio**, reglas puras; **aplicación**, casos de uso; **puertos**, contratos; **adaptadores**, HTTP, persistencia e inferencia; **infraestructura**, configuración y composición. React consume FastAPI mediante Fetch; SQLAlchemy conecta con PostgreSQL.

```text
backend/
  app/
    domain/           # Entidades y reglas de comparación/recomendación
    application/      # Catálogo, comparación y análisis
    ports/            # Contratos de repositorios y servicios
    adapters/         # Entrada HTTP; salida SQL, Excel y ML
    infrastructure/   # Configuración, importación y entrenamiento Python
  alembic/            # Migraciones de base de datos
  data/               # Catálogo y etiquetas de áreas versionados
  models/             # Modelo de áreas y reporte necesarios para la API
  tests/              # Pruebas unitarias y de integración
frontend/
  src/                # Dominio, aplicación, adaptadores, componentes y páginas
    tests/            # Pruebas de interfaz
  public/             # Logos y recursos estáticos
scripts/              # Inicio local en PowerShell
docs/                 # Arquitectura, fuentes, alcance y evaluaciones
.github/workflows/    # Integración continua
```

## Base de datos e InsForge

InsForge se reserva **exclusivamente para alojar PostgreSQL**. FastAPI y SQLAlchemy conservan el acceso a datos mediante `DATABASE_URL` en `backend/.env`, usando `postgresql+psycopg` y las opciones TLS del proveedor.

El proyecto cloud está preparado; la aplicación conserva su conexión local hasta configurar y migrar la base remota. `.insforge/` contiene la vinculación privada de la CLI y está ignorado. `npx -y @insforge/cli db connection-string` obtiene la conexión del proyecto vinculado: contiene una contraseña y debe permanecer en el backend. No se requiere el SDK en React.

PostgreSQL local sigue disponible para desarrollo. Desde la raíz, configura `.env` a partir de `.env.example` y ejecuta `docker compose up -d postgres` si utilizas Docker.

## Instalación y ejecución

Requisitos: Node.js 24, Python 3.12 y acceso a PostgreSQL. Comandos para PowerShell, desde la raíz de un clon:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Configura `DATABASE_URL`, `DATA_MODE=postgres` y `CORS_ORIGINS` en `backend/.env`. Después, desde `backend`:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.infrastructure.cargar_catalogo
.\.venv\Scripts\python.exe -m uvicorn app.infrastructure.principal:app --reload
```

En otra terminal, desde la raíz:

```powershell
cd frontend
npm ci
npm run dev
```

Interfaz: http://localhost:5173 · OpenAPI: http://127.0.0.1:8000/docs. Vite redirige `/api` al backend local. `frontend/.env.example` documenta `VITE_API_URL`, opcional para otra API.

En este equipo preparado, `.\scripts\Iniciar-Orienta.ps1` inicia los servicios locales, aplica migraciones y carga el catálogo. Requiere dependencias y configuración previas.

## Inteligencia artificial: estado real

**Catálogo ampliado:** se conserva íntegro en `backend/data/catalogo_lima_norte_2026.json`. La carga es idempotente y retira de la publicación las 35 ofertas históricas sin borrarlas. Los costos, ingresos y sedes modeladas conservan su procedencia; no son tarifas ni salarios certificados. Consulta la [integración del catálogo](docs/catalogo-completo.md).

**Implementado:** entrenamiento Python de árbol de decisión, random forest y regresión logística con validación y prueba separadas. El modelo histórico, entrenado con 35 ofertas, distingue «misma área / áreas distintas»; no se aplica a las 405 ofertas nuevas sin reentrenamiento y evaluación. Las ofertas relacionadas usan similitud de contenido; las orientaciones y sus motivos se construyen a partir de las fichas.

**Pendiente:** completar las etiquetas revisadas por dos personas y validar el recomendador por criterio según preferencias. Su entrenamiento e integración están preparados; requieren superar el 90% en las cuatro métricas de prueba de cada criterio. Actualmente no hay un recomendador aprendido aprobado. Las explicaciones también necesitan revisión humana.

Desde `backend`, `python -m app.infrastructure.entrenar_modelos` reproduce el clasificador de áreas. El [protocolo de recomendaciones](docs/entrenamiento-recomendaciones.md) describe los comandos del nuevo objetivo; la [evaluación actual](docs/evaluacion-catalogo-ampliado.md) documenta sus límites.

## Verificación y GitFlow

- Frontend, desde `frontend`: `npm test`, `npm run lint`, `npm run build`.
- Backend, desde `backend`: `python -m pytest -q --basetemp=.pytest_tmp` y `python -m ruff check app tests alembic`, usando el entorno virtual.
- Para integración real con PostgreSQL, configura `TEST_DATABASE_URL` con una **base exclusiva de pruebas**: las pruebas modifican su esquema. Sin ella se utiliza SQLite temporal para comportamiento SQL; las pruebas de migraciones y contratos completos requieren PostgreSQL.
- `feature/*` agrupa cambios concretos; los PR se dirigen a `dev`. `main` se reserva para entregas estables. Mantén commits pequeños y verificables.

Se versionan catálogos curados, modelo de ejecución, métricas, migraciones, pruebas, configuración compartida, `.env.example` y dependencias/bloqueos. Se ignoran secretos, cachés y experimentos generados. Más contexto en [docs/](docs/).

## Equipo

Proyecto del curso Diseño de Productos y Servicios — Universidad Tecnológica del Perú.

- Joan Amado Pelayo Soto
- Alexander Huamani Champe
- Martín Rojas Díaz
- Aner Joram Barrenachea Tapia
- Daniel Alexander Benites Villavicencio

Convenciones y compatibilidad: [nomenclatura del proyecto](docs/nomenclatura.md).
