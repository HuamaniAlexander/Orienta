# Evaluación con catálogo ampliado

Clasificador de áreas v1.2.0, 35 ofertas de cinco instituciones. Evaluación nueva con grupos de disciplinas separados y semilla 42. El conjunto de prueba cambió respecto a v1.1; las cifras no miden una mejora sobre un mismo benchmark.

| Algoritmo | Accuracy | Precisión macro | Recall macro | F1 macro |
|---|---:|---:|---:|---:|
| Árbol de decisión | 16.36% | 8.18% | 50.00% | 14.06% |
| Random Forest | 58.18% | 48.93% | 48.19% | 46.15% |
| Regresión logística | 38.18% | 60.47% | 63.04% | 38.00% |

Seleccionado por validación: Árbol de decisión. 276 pares de entrenamiento y 55 de prueba. No habilitado para recomendar: no alcanza el objetivo en las cuatro métricas.

El tamaño reducido y el desajuste entre predictores (costo, duración, modalidad, institución) y área académica impiden justificar resultados altos. No se incorporaron nombres de áreas como predictores ni se escogió al ganador por su resultado en prueba.

Las recomendaciones por criterio son otro objetivo: su código, protocolo y bloqueo de publicación están en [entrenamiento de recomendaciones](entrenamiento-recomendaciones.md). El piloto local contiene 100 comparaciones y 600 filas por revisar, sin etiquetas ni revisores inventados. No hay métricas de recomendaciones aprendidas hasta completar esa revisión.
