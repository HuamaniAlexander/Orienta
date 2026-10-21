# AGENTS.md

## Alcance de ORIENTA

InsForge se reserva exclusivamente para PostgreSQL. Se conservan FastAPI, SQLAlchemy, Alembic y la arquitectura hexagonal. La aplicación utiliza `backend/.env`; las instrucciones genéricas siguientes no autorizan instalar SDKs, activar otros servicios, migrar datos ni cambiar la conexión activa sin una tarea que lo requiera. Nunca versionar `.insforge/` ni credenciales.

## Nomenclatura obligatoria

- Mantener en inglés las carpetas técnicas de arquitectura existentes: `domain`, `application`, `ports`, `adapters`, `infrastructure`, `components`, `hooks`, `pages`, `models` y `tests`.
- Nombrar en español los archivos de funcionalidades, entidades, clases, interfaces, componentes, servicios, repositorios, funciones, métodos, variables, comentarios y documentación propios de ORIENTA.
- React y TypeScript: `PascalCase` para componentes e interfaces; `camelCase` para funciones, variables y hooks propios. Conservar el prefijo técnico `use` de los hooks.
- Python: `snake_case` para módulos, funciones, métodos y variables; `PascalCase` para clases. Usar español en tablas y columnas propias de PostgreSQL.
- No traducir nombres de bibliotecas, imports externos, propiedades HTML, callbacks obligatorios ni convenciones de herramientas: `model_config`, `__tablename__`, `upgrade`, `downgrade`, `conftest.py` y prefijos `test_`, entre otros.
- Conservar rutas, parámetros, claves JSON, códigos de estado, variables de entorno y formatos de artefactos de contratos existentes. Traducir en los adaptadores de borde; el dominio no depende de esos contratos.
- Actualizar importaciones, scripts, pruebas, documentación y referencias con cada renombre. Los cambios de persistencia requieren migraciones reversibles; no reescribir migraciones ya aplicadas.
- Mantener las dependencias dirigidas hacia el dominio. No incorporar frameworks o persistencia al núcleo para facilitar un renombre.

Consultar `docs/nomenclatura.md` para las correspondencias y excepciones de compatibilidad.

<!-- INSFORGE:START -->
## Infraestructura InsForge

[InsForge](https://insforge.dev) se reserva para alojar PostgreSQL. Se mantienen FastAPI, SQLAlchemy y Alembic; los demás servicios de la plataforma quedan fuera del alcance actual.

- **Proyecto:** `orienta-mvp1`, con API base `https://8i7m8jwg.us-east.insforge.app`.
- **Skills instaladas:** consultar la correspondiente antes de utilizar InsForge.
  - `insforge-cli`: proyectos, PostgreSQL, migraciones e infraestructura por CLI.
  - `insforge`: integración de aplicaciones con el SDK, únicamente cuando una tarea la requiera.
  - `insforge-debug`: diagnóstico de fallos y auditorías del servicio.
  - `insforge-integrations`: integración de proveedores externos cuando se solicite.
  - `find-skills`: descubrimiento de skills adicionales.
- **Credenciales:** el backend lee `DATABASE_URL` de `backend/.env`; la CLI usa `.insforge/project.json`. No incrustar ni versionar claves.

Los patrones del SDK y los servicios adicionales no deben introducirse en ORIENTA por defecto. El esquema propio se administra con Alembic y SQLAlchemy.
<!-- INSFORGE:END -->
