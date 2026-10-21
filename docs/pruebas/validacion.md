# Verificación de la entrega

Fecha local de cierre de pruebas: 20/10/2026, America/Lima.

- Backend: 18 pruebas aprobadas con `TEST_DATABASE_URL` apuntando a PostgreSQL 17.11
  local, base exclusiva `orienta_test`. Incluye HTTP sobre persistencia real, migraciones,
  importación, transacciones, catálogo, comparación y modelo entrenado.
- Frontend: 18 pruebas aprobadas en Vitest/Testing Library, build TypeScript estricto y
  lint aprobados. Incluye catálogo/ficha/comparación, filtros, sustitución y fallos IA.
- `ruff check app tests alembic`: aprobado. `pip check`: sin dependencias incompatibles.
- `alembic check`: sin operaciones nuevas; el esquema de PostgreSQL coincide con el ORM.
- `scripts/Iniciar-Orienta.ps1 -NoBrowser`: ejecutado; segunda carga de 19 ofertas sin cambios.
- Navegador: recorrido real selección de dos ofertas → comparación → análisis del modelo
  y alternativas relacionadas, conectado a PostgreSQL. Se revisaron vistas estrecha y
  de escritorio. En escritorio se midieron 1265 px de viewport y 1265 px de contenido,
  sin desbordamiento horizontal en catálogo y comparación/análisis.
- Capturas: `docs/evidencias/catalogo.png`, `comparador.png`, `analisis-ia.png`.

Los resultados de GitHub Actions se consultan en los PR y no se sustituyen por los
resultados locales. La autorización del usuario permite fusionar hacia dev únicamente
cuando no hay conflictos. Cada fusión se hace con SHA esperado, conservando historial.

No se realizaron sesiones con usuarios reales, una auditoría exhaustiva de accesibilidad
ni pruebas de todos los dispositivos. No se afirma rendimiento productivo de la IA.
Existe una advertencia de deprecación de TestClient/httpx en las versiones bloqueadas;
no impide las pruebas y queda registrada sin incorporar una dependencia innecesaria.
