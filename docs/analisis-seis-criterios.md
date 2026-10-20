# Análisis de los seis criterios

El panel principal interpreta duración, modalidad, sede, enseñanza mensual, requisitos
y campo laboral usando los datos de ambas fichas. Expone valores A/B, coincidencias,
diferencias, faltantes, condiciones del dato y una orientación por criterio. No declara
una carrera ganadora ni deduce salarios, empleabilidad o afinidad vocacional.

La explicación estructurada es determinista y se identifica como tal. Las métricas del
clasificador de áreas no son métricas de calidad de esa explicación. La selección de
proveedor generativo sigue pendiente; no se simula un LLM mediante frases predefinidas.

## Evaluación del clasificador versión 1.1.0

Se evaluaron seis configuraciones por algoritmo (18 en total): profundidades y balance
de clases para Árbol/Random Forest; regularización y balance para Regresión logística.
Se elige la menor distancia RMS al vector (1,1,1,1) de accuracy, precisión macro, recall
macro y F1 macro, calculada exclusivamente en validación con grupos separados.
El conjunto de prueba independiente no decide modelo ni hiperparámetros.

El modelo seleccionado fue Árbol de decisión con profundidad 2 y clases balanceadas.
Prueba: accuracy 52,73%, precisión macro 52,71%, recall macro 52,71% y F1 macro 52,71%.
Random Forest y Regresión logística obtuvieron accuracy 50,91% y F1 macro 33,73%.
Se conserva el reporte completo con parámetros y métricas de validación/prueba.

Se requiere al menos 90% en las cuatro métricas externas para habilitar la predicción
como apoyo a decisiones. Esta versión NO alcanza el umbral; la interfaz no la utiliza
para recomendar una carrera. No se alteran etiquetas, se repiten particiones hasta
obtener una cifra favorable ni se incorporan datos de prueba al entrenamiento.

Alcanzar un objetivo requiere un conjunto más amplio y pertinente, con evaluación
independiente. Las 19 ofertas actuales no justifican certificar un 90%. El contraste
documentado de los seis criterios permanece disponible con independencia de ese objetivo.
