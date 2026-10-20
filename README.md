# ORIENTA Compara

Catálogo académico con búsqueda, filtros, fichas trazables, comparación de dos ofertas,
clasificador de contraste académico entrenado y alternativas relacionadas por contenido.
No requiere cuentas. React/TypeScript comunica con FastAPI mediante Fetch; PostgreSQL
persiste las ofertas, sus fuentes y las importaciones. El núcleo aplica arquitectura hexagonal.

## Inicio en este equipo Windows

Las dependencias y PostgreSQL local ya se prepararon en este espacio. Desde la raíz:

```powershell
.\scripts\Start-Orienta.ps1
```

Abre http://127.0.0.1:5173. El script inicia servicios ocultos si están detenidos, aplica
migraciones e importa de forma repetible el catálogo versionado. No instala software.
Los logs quedan en `.local/`. El PostgreSQL descargado y sus credenciales son locales,
no se versionan. No se configura un servicio de Windows ni inicio automático.

Para iniciar solo la API y la interfaz manualmente, en dos terminales:

```powershell
cd backend
$env:DATA_MODE="postgres"
.\.venv\Scripts\python.exe -m uvicorn app.infrastructure.main:app --reload
```

```powershell
cd frontend
npm run dev
```

## Instalación desde otro clon

Requiere Node.js 24, Python 3.12 y PostgreSQL 17 (directo o con Docker Compose).

1. Copia `.env.example` a `.env`, configura credenciales y ejecuta `docker compose up -d postgres`.
2. Desde `backend`: crea un entorno con `python -m venv .venv`, actívalo e instala
   `python -m pip install -r requirements-dev.txt`.
3. Copia `backend/.env.example` a `backend/.env`; configura `DATABASE_URL` para tu PostgreSQL.
   No publiques contraseñas. `DATA_MODE=postgres` es el modo normal.
4. Desde `backend`: `python -m alembic upgrade head` y `python -m app.infrastructure.seed_catalog`.
5. Desde `backend`: `python -m uvicorn app.infrastructure.main:app --reload`.
6. Desde `frontend`: `npm ci` y `npm run dev`. El proxy `/api` apunta a 127.0.0.1:8000.
   `VITE_API_URL` puede configurar una API diferente; CORS se configura en el backend.

En Windows puedes usar directamente `.venv\Scripts\python.exe` sin activar el entorno.
OpenAPI: http://127.0.0.1:8000/docs. pgAdmin es opcional: `docker compose up -d pgadmin`.
Los contenedores Compose originales solo cubren PostgreSQL/pgAdmin; API y frontend se
ejecutan con los comandos anteriores.

## Datos y ampliación del catálogo

Hay 19 ofertas de UTP y UNMSM extraídas del Excel suministrado. Se preservan sedes,
modalidades, duración en meses, enseñanza mensual en soles, fuentes y fechas. Un cero
explícito es diferente de un dato faltante. Los costos estimados no son tarifas oficiales;
enseñanza gratuita no significa ausencia de otros gastos.

Importa nuevos registros documentados desde un Excel con el mismo esquema:

```powershell
cd backend
python -m app.infrastructure.import_excel "C:\ruta\ORIENTA_Datos_PoC.xlsx"
```

Valida todo el libro antes de escribir, evita duplicados por código e identidad académica
y confirma una sola transacción. Repetir un archivo sin cambios no duplica registros.
Las ofertas ausentes en una importación no se retiran automáticamente. `active=false`
retira una oferta del catálogo y del comparador; la administración editorial no tiene
un endpoint público de escritura.

El adaptador JSON de solo lectura permanece para pruebas aisladas (`DATA_MODE=demo`);
no reemplaza automáticamente a PostgreSQL cuando este falla. La página normal utiliza
PostgreSQL. Los datos de entrenamiento no se amplían con carreras inventadas.

## Entrenamiento y análisis IA

El modelo ya está versionado. Para repetir el entrenamiento desde `backend`:

```powershell
python -m app.infrastructure.train_models
```

Entrena tres algoritmos, selecciona por validación con grupos de carreras separados y
evalúa en grupos externos. Guarda `models/model.joblib` y `models/metrics.json`.
No entrena durante solicitudes HTTP. Para nuevas ofertas, actualiza también
`data/catalog.json` y `data/areas.json` con áreas, grupos y fuentes documentados.
Reinicia la API después de versionar un nuevo modelo.

El clasificador distingue áreas académicas, no aptitudes ni carrera ideal. La evaluación
actual no alcanza el objetivo del 90%; métricas y limitaciones se muestran en
la interfaz. Las alternativas relacionadas usan TF-IDF y similitud de contenido.
El resumen y los siguientes pasos son deterministas; no se simula un LLM generativo.
No se usan servicios IA externos ni claves. Consulta [el informe del modelo](docs/modelo-ia.md).

## Pruebas

Frontend, desde `frontend`: `npm run build`, `npm run lint`, `npm run test`.

Backend, desde `backend`: `python -m pip check`, `python -m ruff check app tests alembic`,
`python -m pytest -q --basetemp=.pytest_tmp`, `python -m alembic check`.

Para integración con PostgreSQL configura `TEST_DATABASE_URL` con una base exclusiva
de pruebas: la suite aplica y revierte migraciones en esa base. Nunca uses una base
con datos que quieras conservar. Si falta esa variable, las pruebas SQL locales usan
SQLite temporal y no certifican PostgreSQL. GitHub Actions siempre suministra un
PostgreSQL 17 dedicado.

## API y estructura

- `GET /api/carreras`: búsqueda, filtros combinados y paginación; solo ofertas activas.
- `GET /api/filtros`, `GET /api/carreras/{id}`, `GET /api/salud`.
- `POST /api/comparaciones`: `{ "career_ids": ["C01", "C02"] }`.
- `POST /api/comparaciones/analisis`: mismo cuerpo; predicción, contraste documentado,
  métricas y alternativas relacionadas. Fallos IA no eliminan la comparación.

`backend/app/domain` contiene reglas puras; `application`, casos de uso; `ports`,
contratos; `adapters/input`, HTTP; `adapters/output`, SQL/Excel/ML; `infrastructure`,
composición y comandos. Los modelos ORM y esquemas HTTP no son entidades del dominio.
Frontend separa tipos/reglas, acceso HTTP, estado de aplicación, componentes y páginas.

`dev` es integración; las ramas feature se incorporan por PR. `main` se reserva para
una entrega futura. No hay despliegue de producción ni release. La trazabilidad y
las limitaciones académicas se documentan en `docs/`; las pruebas de usabilidad reales,
matrices ponderadas y revisión institucional siguen pendientes del equipo.
# Actualización del catálogo y recomendaciones

El catálogo contiene 35 ofertas de cinco universidades. Los logos y nombres completos aparecen en catálogo, fichas y comparación. La comparación acepta preferencias y explica sus seis criterios con motivos y fuentes.

El entrenamiento supervisado por criterio y su protocolo están en [docs/entrenamiento-recomendaciones.md](docs/entrenamiento-recomendaciones.md). El piloto requiere revisión humana; no se han generado etiquetas ni porcentajes ficticios. La evaluación actual del clasificador de áreas está en [docs/evaluacion-catalogo-ampliado.md](docs/evaluacion-catalogo-ampliado.md). Las cifras de 19 ofertas que siguen en este documento corresponden al alcance histórico inicial.

