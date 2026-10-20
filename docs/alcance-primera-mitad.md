# Primera mitad funcional de ORIENTA

Alcance acordado por interpretación del pedido del 19/10/2026: HU01, HU02 y HU03,
con persistencia e importación necesarias. Es aproximadamente la mitad del producto,
no una certificación de 40 tarjetas completas ni de avance del tablero Trello.

## Auditoría inicial

`dev` partía de f33ba07: dependencias y carpetas, sin rutas React, tablas, migraciones,
importador, casos de uso o pruebas funcionales. `main` solo contenía un README.
Las diez ramas feature apuntaban a la misma preparación. No había AGENTS.md.
ORI-001 y la base técnica tienen evidencia en Git; permisos, protecciones y estado
de Trello (ORI-002/003/005/006) no se dan por verificados.

Se revisaron CSV de 80 tareas, guía S10, informe APF2, actividad S9 y Excel.
Los ejemplos e instrucciones académicas son contexto; no amplían el pedido del usuario.
Las 17 pantallas son referencia visual, no prueba de funciones existentes.

## Entrega y dependencias

1. `feature/arquitectura-hexagonal`: contratos, diagrama y decisiones (ORI-007/008/009/010).
2. `feature/base-datos`: modelo, Alembic e importación validada (ORI-013 a ORI-018).
3. `feature/backend-core`: dominio, puertos, catálogo y detalle HTTP (ORI-021 a ORI-025/027).
4. `feature/hu01-catalogo`: navegación, tarjetas, conexión y estados (ORI-028 a ORI-033).
5. `feature/hu02-busqueda-filtros`: búsqueda combinada, filtros y pruebas (ORI-034 a ORI-038).
6. `feature/hu03-ficha-carrera`: seis criterios, fuentes y faltantes (ORI-039 a ORI-043).

Las ramas se encadenan conservando sus dependencias mediante merge local, sin fusionar
PR ni modificar `dev`. Los PR hacia `dev` deben revisarse e integrarse en este orden.
La última rama permite probar el conjunto antes de la integración del equipo.

Se adelantan pruebas, responsive, accesibilidad y CI (partes de ORI-051/053/067/068/069/074)
porque acompañan las funcionalidades, sin declarar esos bloques completos.
ORI-026 se difiere junto al comparador ORI-044 a ORI-050; no tiene consumidor en este corte.
No se implementan IA, cuestionarios, cuentas ni recomendaciones vocacionales.
Matrices ponderadas ORI-011 y pruebas con usuarios reales quedan pendientes del equipo.

## Contratos HTTP

- `GET /api/salud`: disponibilidad del proceso (no certifica la base de datos).
- `GET /api/carreras?q=&tipo=&modalidad=&ubicacion=&pagina=1&limite=12`:
  `{ items, total, pagina, limite }`, solo ofertas activas, orden nombre/institución/id.
- `GET /api/filtros`: valores de filtros de todas las ofertas activas.
- `GET /api/carreras/{id}`: oferta y fuentes; 404 si no existe o está retirada.
- Validación HTTP: 422; indisponibilidad de persistencia: 503 sin datos internos.

El dominio no importa frameworks. Los controladores delegan en casos de uso; SQLAlchemy
implementa un puerto y transforma modelos ORM a entidades. La sesión dura una solicitud.
La importación valida todo el libro antes de escribir y hace una transacción completa.

## Datos y decisiones

El libro entregado tiene una hoja Carreras, 19 registros y 38 columnas, incluidas
codificaciones para ML que no deben interpretarse como valores académicos.
No contiene tipo de formación explícito: las instituciones UTP, UNMSM, UNI y UPCH
se clasifican mediante un mapeo documentado como universitarias; cualquier institución
desconocida conserva tipo no disponible. No se inventan ofertas técnicas para llenar filtros.
Ubicación conserva el texto original: no se infiere distrito de una sede.
Costos en soles mensuales y duración en meses; cero explícito se conserva.
Estados y fecha proceden del libro, no de una nueva verificación institucional.
Requisitos y campo laboral sin estado explícito se presentan como datos de la PoC.

PostgreSQL es la persistencia de producción/local normal. El modo `demo` es un adaptador
de lectura de una instantánea JSON extraída del Excel, sin escrituras, con aviso visible.
No se activa automáticamente cuando falla PostgreSQL. Nunca se presenta como prueba de BD.
La instantánea se genera con el mismo lector validado del importador y se versiona para
una demo reproducible. No se copia el libro completo ni datos de entrenamiento.
