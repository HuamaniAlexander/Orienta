# Orientación vocacional y aprendizaje de preferencias

## Estado y alcance

El usuario confirmó que aún no dispone de elecciones reales etiquetadas. **No existe un recomendador de preferencias entrenado en producción, ni métricas reales de ese objetivo.** La funcionalidad implementa el cuestionario, integración PostgreSQL, captura voluntaria, revisión, entrenamiento reproducible, inferencia y explicaciones. Sin un artefacto evaluado, responde `sin_modelo`; no usa reglas para simular una recomendación aprendida.

El clasificador histórico de áreas y las orientaciones estructuradas de seis criterios siguen disponibles por separado. Sus métricas no evalúan el nuevo objetivo.

## Arquitectura y contratos

- Dominio: `cuestionario.py`, `perfil_vocacional.py`; definiciones y características puras, independientes de frameworks.
- Aplicación: `recomendar_preferencia.py`; valida el par, obtiene las fichas del catálogo, prepara preguntas, valida respuestas y coordina captura e inferencia.
- Puertos: `motor_preferencias.py`; inferencia y registro se desacoplan del caso de uso.
- Adaptadores: `vocacional.py` (HTTP/Pydantic), `registro_preferencias.py` (SQLAlchemy) y `motor_preferencias.py` (scikit-learn local).
- Infraestructura: entrenamiento y revisión/exportación offline. El ciclo normal de la API nunca entrena.

Nuevos endpoints, con campos JSON en español y camelCase:

| Endpoint | Función |
| --- | --- |
| `GET /api/v1/cuestionario` | Seis preguntas generales y versión |
| `GET /api/v1/cuestionario/comparativo?idsProgramas=…&idsProgramas=…` | Diez preguntas para exactamente dos ofertas vigentes |
| `POST /api/v1/recomendaciones` | Valida respuestas, captura opcional e inferencia local |

OpenAPI publica solicitudes y respuestas tipadas. Los contratos anteriores se conservan. React reutiliza el transporte HTTP; los nuevos contratos no pasan por las traducciones de claves inglesas de la API histórica.

La migración `0004` crea `definiciones_cuestionario` y `registros_preferencias`. Las características y condiciones académicas se reutilizan desde las ofertas existentes; no se duplican tablas de carreras. El artefacto y su informe contienen la versión y metadatos del modelo, por lo que no se añade una tabla de versiones sin consumidor.

## Preguntas y características

Las preguntas 7–9 utilizan cursos, actividades y habilidades documentadas. Si son la misma carrera o los contenidos no se distinguen, comparan modalidad/sede, formación/duración y condiciones institucionales, identificando la limitación del catálogo. Siempre muestran nombres de carrera e institución. No generan cursos inventados.

| Característica | Definición relativa entre ofertas |
| --- | --- |
| Intereses | Correspondencias de cinco respuestas con seis familias orientativas de contenido académico |
| Habilidades | Respuesta de habilidad y contenido de las fichas |
| Materias, actividades, problemas/formación | Preferencias declaradas en preguntas dinámicas |
| Costo | Compatibilidad con presupuesto o diferencia normalizada si se prioriza costo |
| Duración | Compatibilidad con límite de tiempo o diferencia normalizada si se prioriza duración |
| Modalidad | Coincidencia con la modalidad indicada |

El vocabulario RIASEC es una correspondencia orientativa explícita, **no un instrumento psicológico validado**. «Incierto» no produce una valoración negativa: omite evidencia; «ambas» representa igualdad relativa y «ninguna» no se confunde con incertidumbre. Si ninguna propuesta interesa en las tres preguntas comparativas, se invita a ampliar el catálogo. Sin preferencias suficientes no se fuerza inferencia. No se infiere empleabilidad de salarios o demanda modelados.

Se usa un orden canónico de identificadores, diferencias antisimétricas, escalado sin centrar y regresión logística sin intercepto. Intercambiar las ofertas cambia el signo del margen, manteniendo la misma carrera elegida. Las contribuciones son `coeficiente × característica escalada` y suman el margen exacto. No se muestran probabilidades como confianza ni porcentajes de éxito profesional. Un margen absoluto inferior a 0.2 se presenta como afinidad similar; es una política explícita, no una equivalencia psicológica validada.

## Captura y revisión

Los visitantes pueden analizar sin guardar respuestas. El aporte es opcional, separado y restringido a quienes declaran mayoría de edad y dan consentimiento. No se solicitan nombres, correo, fecha de nacimiento ni documentos. El identificador aleatorio de participante se conserva solo durante la sesión del navegador, sin huella del dispositivo.

Antes del primer resultado se solicita una elección independiente; no se copia una respuesta del cuestionario ni una predicción a la etiqueta. El registro se escribe antes de inferir y queda `pendiente`. Reintentos idénticos son idempotentes. Después del primer análisis de esa sesión de cuestionario no se ofrece capturar una etiqueta influida por el resultado.

El seudónimo no demuestra que dos navegadores correspondan a personas diferentes. La mayoría de edad es declarada. La revisión del equipo debe verificar procedencia real, consentimiento, independencia, calidad y duplicidades; no basta con aprobar automáticamente la captura. Los menores pueden usar el cuestionario sin aportar datos de entrenamiento. Las fichas se guardan como instantáneas para auditoría; una huella canónica detecta cambios antes de entrenar.

No hay endpoints públicos para listar, revisar ni exportar capturas. PostgreSQL tiene RLS y privilegios retirados para roles `anon`, `authenticated` y `PUBLIC` sobre tablas propias; FastAPI usa la conexión de servidor. La reversión de `0004` retira las tablas nuevas; no restablece privilegios públicos revocados. Revisar permisos explícitamente si se revierte el despliegue.

## Operación offline

Desde `backend`, con el entorno virtual y `DATABASE_URL` privado:

```powershell
python -m app.infrastructure.gestionar_preferencias revisar --id UUID --estado aprobado --motivo "Consentimiento y elección independiente comprobados por el equipo"
python -m app.infrastructure.gestionar_preferencias exportar --salida data/preferencias/revisadas.jsonl
python -m app.infrastructure.entrenar_preferencias --datos data/preferencias/revisadas.jsonl --salida models/preferencias
```

No ejecutar aprobación sin revisión real. El código de captura permite al participante identificar su aporte ante el equipo para solicitar su retirada. El operador puede ejecutar `python -m app.infrastructure.gestionar_preferencias retirar --id UUID --confirmar`; elimina ese aporte y requiere la confirmación explícita del operador. Excluirlo también de exportaciones conservadas y reentrenar cualquier versión que lo hubiera utilizado. Definir un plazo de conservación antes de recopilar una muestra pública. Las exportaciones y modelos generados están ignorados por Git; no publicar respuestas ni etiquetas de participantes.

Para reentrenar, usa un directorio nuevo (por ejemplo `models/preferencias-v2`): el comando rechaza sobrescribir versiones. Revisa su informe y conserva la versión anterior antes de activar el directorio `models/preferencias` consumido por la API. El adaptador comprueba hash, esquema y habilitación; ante ausencia, corrupción o métricas insuficientes se abstiene.

## Evaluación y límites

Se requiere un mínimo operativo de 30 participantes con etiquetas revisadas de elección única; no es garantía de representatividad. Las etiquetas ambas/ninguna/incierto se conservan en los registros, pero se excluyen de la clasificación binaria. División 60/20/20 por participante con semillas 42/43, sin participantes compartidos y con ambas clases en cada partición. Si falta cobertura, se rechaza el entrenamiento en lugar de cambiar la partición para mejorar métricas.

Solo entrenamiento recibe pares invertidos. Se elige `C` entre 0.1, 1 y 10 con F1 macro de validación. La prueba se reserva para la evaluación final: accuracy, balanced accuracy, precisión/recall/F1 macro, matriz de confusión y Brier. Se compara con una clase mayoritaria. La habilitación requiere superar 0.90 en accuracy, precisión, recall y F1 de prueba y mejorar la referencia. Es un objetivo pendiente, no una cifra obtenida.

El informe registra Python, scikit-learn, esquema, semillas, tamaños de particiones, versión y SHA-256. Las pruebas incluyen fixtures sintéticas temporales exclusivamente para verificar el pipeline, separación, reproducibilidad y contribuciones; **no constituyen estudiantes ni evidencia de rendimiento real**, y sus artefactos no se activan en la aplicación.
