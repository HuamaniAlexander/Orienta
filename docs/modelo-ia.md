# Contraste académico y alternativas relacionadas

Este documento describe la versión inicial 1.0.0. La versión actual 1.1.0 y su nuevo
criterio de selección se documentan en `analisis-seis-criterios.md`; sus métricas se
obtienen de `backend/models/metricas.json`. Las cifras históricas siguientes no son
la evaluación de la versión actual.

Se entrenaron Árbol de decisión, Random Forest y Regresión logística usando las 19
ofertas y sus áreas/grupos documentados en el Excel suministrado. La etiqueta indica
misma área o áreas distintas. No mide afinidad vocacional ni empleabilidad.

`python -m app.infrastructure.entrenar_modelos` ejecuta el entrenamiento fuera de HTTP.
Se usa semilla 42, se dividen grupos antes de construir pares y se descartan pares
que cruzan conjuntos. Hay 8 ofertas/28 pares de entrenamiento y 11 ofertas/55 pares de
prueba. La validación interna también separa grupos antes de construir sus pares.
Las matrices de confusión usan el orden [misma área, áreas distintas].

La selección usa exclusivamente F1 macro medio de validación. En esta ejecución hubo
empate entre los tres modelos; se conserva el primero declarado, Árbol de decisión,
como criterio determinista. El conjunto de prueba no decide la selección. El artefacto
supervisado conserva el ajuste al conjunto de entrenamiento, sin volver a entrenar
con los grupos de prueba.

Resultado de esta ejecución: accuracy 49,09%, precisión macro 41,67%, recall macro
48,28% y F1 macro 35,83%. La referencia de clase mayoritaria obtuvo 50,91% de accuracy.
El resultado NO demuestra utilidad predictiva; la interfaz lo muestra como experimental
y prioriza los metadatos del catálogo ante discrepancias. No se reutilizan las métricas
del informe S9, porque el código y la validación han cambiado.

Los predictores son diferencias/promedios de costo mensual y duración, institución y
modalidad de ambos lados. Los nombres, áreas, grupos y códigos identificadores se
excluyen de las entradas. El orden canónico del par garantiza simetría al intercambiarlo.
El preprocesamiento se ajusta dentro de cada partición, con imputación, escalado y
codificación categórica. `models/metricas.json` registra grupos, métricas de los tres
modelos, matrices, baseline, firmas de ofertas y hashes de catálogo/artefacto.

Un segundo componente no supervisado ajusta TF-IDF sobre nombre, campo laboral y
requisitos del catálogo. Sugiere otras ofertas por similitud de contenido; no usa
resultados personales ni afirma que sean adecuadas para un estudiante. No hay
evaluación de utilidad con usuarios y no se presentan porcentajes de afinidad.

El resumen numérico y los siguientes pasos son texto determinista identificado como
orientaciones sobre los datos. NO se presentan como texto generado por un LLM.
No se ha contratado ni simulado un proveedor generativo. El análisis no envía datos
a terceros, no requiere claves y no agrega costo por solicitud.

La carga se limita al artefacto local versionado, verificando SHA-256 antes de joblib.
No se aceptan modelos enviados por HTTP. Las firmas de las ofertas detectan cambios
de datos que requieren reentrenamiento. El modelo se carga una vez por proceso; no
se entrena en solicitudes. Si falta o falla, la comparación continúa disponible y la
interfaz permite reintentar. Para adoptar un LLM generativo futuro se requiere una
decisión del equipo sobre costo, privacidad, evaluación y fuentes.
