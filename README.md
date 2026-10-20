# ORIENTA — MVP 1

Base técnica de ORIENTA Compara. Todavía no incluye funcionalidades, datos, modelos entrenados ni proveedor de IA.

## Requisitos
Node.js 24 LTS, Python 3.12, Docker con Compose (para PostgreSQL y pgAdmin).

## Inicio local
1. Copiar `.env.example` a `.env` y cambiar las contraseñas de ejemplo.
2. Ejecutar `docker compose up -d`.
3. Frontend: `cd frontend`, `npm ci`, copiar `.env.example` a `.env`, `npm run dev`.
4. Backend: desde `backend`, `python -m venv .venv`, activar el entorno, `python -m pip install -r requirements-dev.txt`, copiar `.env.example` a `.env` y ajustar la contraseña.
5. Desde `backend`: `uvicorn app.infrastructure.main:app --reload`.

Frontend: http://localhost:5173. API/OpenAPI: http://localhost:8000/docs. pgAdmin: http://localhost:5050; registrar servidor con host `postgres`, puerto 5432 y credenciales de `.env`.

## Estructura
- `frontend/`: React, TypeScript, Vite, Tailwind, React Router y Vitest/Testing Library.
- `backend/app/domain/`: entidades y reglas puras, independientes de frameworks.
- `backend/app/application/`: futuros casos de uso.
- `backend/app/ports/`: futuros contratos de entrada/salida.
- `backend/app/adapters/input/` y `output/`: HTTP, persistencia, Excel y servicios externos.
- `backend/app/infrastructure/`: composición y arranque FastAPI.
- `backend/alembic/`: reservado para las migraciones; inicialización y esquema pendientes en feature/base-datos.
- `docs/`: documentación por área.

Se usará Fetch API (nativa del navegador); no se necesita Axios para el alcance actual. pandas, NumPy, scikit-learn y openpyxl preparan la futura integración de la PoC. No se ha escogido proveedor de IA. Playwright se evaluará cuando existan recorridos funcionales.

## Verificación
Frontend: `npm run build`, `npm run lint`, `npm run test` (cuando existan pruebas).
Backend: `python -m pip check`, `ruff check app`, `pytest` (cuando existan pruebas).
No hay pruebas funcionales en esta base. No se incluyen tablas ni importación de datos.

## Ramas
`main` conserva su estado previo. `dev` es la rama de integración (equivalente a develop), por indicación del equipo. Las ramas feature parten del commit de preparación de dev y se integrarán mediante PR hacia dev. Actualizar cada feature con dev antes de empezar porque las ramas no se sincronizan automáticamente.

Ramas previstas: arquitectura-hexagonal, base-datos, backend-core, hu01-catalogo, hu02-busqueda-filtros, hu03-ficha-carrera, hu04-comparador, hu05-vista-ligera, hu-ia01-explicacion y pruebas-pdca, todas con prefijo `feature/`.
La configuración inicial queda completada directamente en dev; release/* y hotfix/* se crearán cuando exista una entrega o corrección que preparar.

No subir `.env`, entornos virtuales ni node_modules. Las dependencias se reinstalan desde los archivos de versiones del repositorio.

## Validación de esta preparación
Compilación y lint del frontend correctos. `pip check` correcto y consulta de OpenAPI mediante TestClient correcta. Docker no está disponible en el entorno de preparación, por lo que los contenedores no se arrancaron. Ruff quedó instalado pero su binario falló en este entorno (segmentation fault); su ejecución debe verificarse en local. Las pruebas funcionales se incorporarán con las funcionalidades.
Los locks Python se generaron en Linux con Python 3.12; `uvloop` es opcional y se omite en Windows.
