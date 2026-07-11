# Arquitectura del sistema

## Componentes

El sistema se organiza en dos etapas: recuperacion y clasificacion.

### Recuperacion

Dado un articulo o fragmento de consulta, se buscan los articulos del corpus mas relacionados mediante tres estrategias:

- Lexica, con el algoritmo BM25 sobre el texto tokenizado de cada articulo.
- Densa, con embeddings del modelo BAAI/bge-m3 (1024 dimensiones), indexados en una base de datos vectorial Qdrant con similitud coseno.
- Hibrida, combinando los puntajes normalizados de las dos anteriores, con un peso de 0.6 para la componente densa.

### Clasificacion

Cada par (articulo de consulta, articulo recuperado) se pasa a un clasificador que determina la relacion normativa entre ambos, en una de cinco categorias: contradiccion, compatibilidad, especificacion, excepcion o ausencia de relacion.

Se evaluaron dos variantes del clasificador:

- Zero shot, usando directamente un modelo NLI multilingue preentrenado (MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7), sin ajuste adicional. Este modelo tiene tres clases nativas (entailment, neutral, contradiction), por lo que para compararlo contra el gold set de cinco clases se aplica un mapeo: contradiccion y excepcion se agrupan como contradiction, especificacion como entailment, compatibilidad y ausencia de relacion como neutral.
- Ajustada con LoRA, reemplazando la cabeza de clasificacion del mismo modelo base por una nueva de cinco salidas, y entrenando esa cabeza junto con adaptadores de bajo rango sobre las capas de atencion, usando un conjunto de 211 pares construidos a partir de articulos reales del corpus.

## Diseño experimental

Se separa explicitamente el error atribuible a la recuperacion del atribuible a la clasificacion, evaluando cada clasificador en dos condiciones: contra el par correcto conocido del gold set (sin pasar por el retriever), y contra el candidato que efectivamente devuelve el retriever en un uso real del sistema. La diferencia entre ambas condiciones mide el costo del error de recuperacion.

## Justificacion de las decisiones de diseño

El modelo NLI se eligio multilingue, y no uno entrenado exclusivamente en ingles, porque se verifico experimentalmente que el idioma de entrenamiento afecta el desempeno sobre texto juridico en español, incluso siendo el modelo multilingue de menor tamaño.

El conjunto de entrenamiento para el ajuste fino se construyo sobre articulos reales del corpus, y no sobre oraciones sinteticas cortas, porque un primer intento con oraciones sinteticas (de 7 a 8 palabras en promedio) produjo un modelo con desempeno nulo sobre el gold set real, cuyos articulos promedian entre 33 y 52 palabras. Este intento fallido se documenta en `docs/experimento_baseline_fallido.md`.
