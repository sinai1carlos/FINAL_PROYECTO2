# Experimento de linea base: ajuste fino fallido con modelo en ingles

## Que se hizo

El primer intento de este proyecto aplico ajuste fino con LoRA sobre `cross-encoder/nli-deberta-v3-large`, un modelo NLI entrenado exclusivamente en ingles (SNLI y MultiNLI), reemplazando su cabeza de clasificacion por una de cinco salidas. El conjunto de entrenamiento usado fue `dataset_5clases_sintetico.json`, compuesto por 2500 pares sinteticos (500 por clase), con oraciones cortas de 7 a 8 palabras en promedio.

Cuaderno: `notebooks/lora_baseline_ingles_fallido.ipynb`.

## Que resultado dio

Evaluado sobre el gold set real (articulos completos del Codigo Civil, de 33 a 52 palabras en promedio), el modelo obtuvo F1 de 0 en varias de las cinco clases, incluyendo contradiccion. El modelo zero shot, sin ningun ajuste fino, obtuvo mejor desempeno que el modelo ajustado.

## Por que fallo

Se identificaron dos causas:

1. Desajuste de idioma: el modelo base nunca fue entrenado con texto en español para la tarea de NLI.
2. Desajuste de estilo y longitud: las oraciones sinteticas de entrenamiento no se parecen al texto legal real, que incluye incisos, remisiones a otros articulos y clausulas de excepcion. El modelo aprendio patrones lexicos superficiales de las oraciones cortas que no transfieren al texto real.

## Que se cambio a partir de este resultado

El segundo intento (`notebooks/lora_5clases_multilingue.ipynb`) cambia dos variables: se usa un modelo NLI multilingue con cobertura de español, y se reemplaza el conjunto de entrenamiento sintetico por uno construido sobre 211 articulos reales del corpus, verificado sin superposicion con el gold set de evaluacion.

Este experimento se conserva en el repositorio como evidencia del proceso iterativo del proyecto y como linea base adicional de comparacion.
