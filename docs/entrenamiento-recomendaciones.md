# Recomendaciones supervisadas por criterio

El objetivo nuevo es clasificar cada criterio según las preferencias declaradas del estudiante. No sustituye ni modifica las etiquetas del experimento de áreas de la Actividad 09.

Etiquetas: `favor_left`, `favor_right`, `equivalent`, `needs_preference`, `insufficient_data`. Left/right son identificadores internos: la interfaz usa los nombres de carrera e institución.

## Preparar y revisar

Desde backend:

```powershell
.venv/Scripts/python.exe -m app.infrastructure.recommendation_training --prepare
.venv/Scripts/python.exe -m app.infrastructure.recommendation_training
```

El primer comando crea un piloto sin respuestas automáticas: hasta 100 comparaciones, seis etiquetas por comparación, particiones 60/20/20 y ofertas disjuntas. No volver a ejecutar sobre anotaciones revisadas: usar `--dataset` para otra salida.

Dos integrantes distintos deben revisar cada criterio, registrar sus etiquetas por separado, una justificación y las fuentes pertinentes. Las discrepancias requieren `adjudication`. Ninguna etiqueta se marca aprobada automáticamente. Registrar preferencias explícitas en `preferences`: presupuesto mensual, máximo de meses, modalidad, sede, requisitos que cumple y actividades laborales de interés. No adjudicar un ganador cuando falta una preferencia determinante o un dato necesario. Mantener los mismos perfiles de preferencia en las particiones sin copiar comparaciones.

El piloto comprueba el protocolo; no basta para habilitar el modelo. El entrenamiento exige al menos cinco ejemplos de cada clase, criterio y partición. Eso implica ampliar y equilibrar el corpus revisado según los casos reales, sin replicar filas para alcanzar mínimos. Congelar la prueba antes de ajustar hiperparámetros. Si se estudian variantes de una carrera, asignarlas juntas a una partición antes de revisar; el validador comprueba además ofertas y pares duplicados.

## Evaluar

Se ajustan nueve candidatos por criterio: árbol, random forest y regresión logística con tres configuraciones. La selección usa únicamente distancia a 1 en accuracy, precisión macro, recall macro y F1 macro de validación. El vocabulario se aprende solo en entrenamiento; nombres, identidades, fuentes, etiquetas y explicaciones no son predictores.

El conjunto de prueba se utiliza una vez para medir el ganador. Se guarda matriz de confusión, tamaños, candidatos, huella del corpus y del artefacto. Todas las cuatro métricas de cada uno de los seis criterios deben superar 0.90. Un fallo impide aprobar el conjunto. El artefacto experimental no se despliega automáticamente. Evaluar además las justificaciones con revisión humana: respaldo factual, utilidad y ausencia de conclusiones no sustentadas; las métricas de clasificación no certifican la calidad del texto.

Actualmente no hay etiquetas humanas revisadas. El comando rechaza el piloto vacío de etiquetas y no genera métricas ni modelos falsos. La aplicación conserva explicaciones estructuradas verificables, identificadas como tales; no presenta esas reglas como recomendaciones aprendidas. La integración de predicciones requiere corpus revisado, evaluación satisfactoria y validación de las explicaciones.
