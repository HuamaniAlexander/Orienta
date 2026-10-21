# Sistema visual Vichy

`frontend/src/tokens.css` centraliza la paleta: gris claro `#BBBFBF`, gris medio `#878787`, acento `#05AD98`, blanco `#FFFFFF`, texto `#172B2C`, secundario `#526263`, fondo `#F6F8F8`, bordes `#D9DEDE` y acción `#087568`. Los textos pequeños y botones usan el turquesa oscuro accesible; el acento se reserva para indicadores. Los colores de marcas institucionales y avisos semánticos conservan su significado.

Se mantienen la composición del comparador y los contratos funcionales. El contenido utiliza una fuente general legible y los títulos una fuente monoespaciada local. La escala base es de 8 px; botones y campos tienen al menos 44–48 px. Tarjetas blancas, bordes discretos y controles de foco visibles. Las transiciones respetan movimiento reducido.

Inicio y Mi orientación tienen rutas reales; la navegación conserva Explorar, Comparar e Instituciones. El cuestionario usa un solo componente de pregunta, radios accesibles, progreso y navegación con respuestas conservadas. No depende del color para indicar selección.

Las fotografías ilustrativas por profesión se generaron para ORIENTA; no representan estudiantes ni instalaciones de las instituciones. Se guardan en WebP, se cargan de forma diferida con dimensiones declaradas, `object-fit: cover`, encuadre superior y respaldo. No se cambian proporciones de logotipos. Las familias agrupan carreras afines: no implican una foto exclusiva para cada una de las 405 ofertas.

La comprobación visual cubre 1920×1080, 1440×900, 1024×768, 768×1024 y 390×844, revisando Inicio, catálogo, ficha, comparación, instituciones y cuestionario. Las capturas de revisión se conservan localmente en `.references/`; no contienen respuestas reales de participantes. Las tablas y la navegación horizontal desplazan únicamente su contenedor cuando corresponde, evitando desbordamiento de la página.
