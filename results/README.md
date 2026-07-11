# Resultados

Todas las cifras de este archivo corresponden a corridas efectivamente ejecutadas y verificadas durante el desarrollo del proyecto, salvo el archivo marcado como pendiente.

## Ya verificado

- `ablation_3clases_gold_natural.csv`: comparacion de las cuatro configuraciones (linea base de coseno, NLI con par correcto, RAG denso mas NLI, RAG hibrido mas NLI) sobre el gold set natural de 142 pares, agrupado en tres clases. Incluye intervalos de confianza al 95 por ciento obtenidos por bootstrap.
- `ablation_3clases_gold_balanceado.csv`: la misma comparacion sobre un gold set balanceado de 81 pares (27 por clase), usado como analisis de robustez frente al desbalance de clases del conjunto natural.
- `metricas_retriever.csv`: Recall@5, Recall@10, Recall@15 y porcentaje de citas correctas en la primera posicion, para los tres metodos de recuperacion evaluados.
- `comparacion_idioma_modelo_nli.csv`: comparacion entre un modelo NLI entrenado solo en ingles y un modelo NLI multilingue, sobre la misma tarea.
- `exploraciones_adicionales.csv`: nueve configuraciones adicionales evaluadas para intentar mejorar el sistema de extremo a extremo (segmentacion de texto, agregacion de multiples candidatos, tres modelos de reordenamiento). Ninguna mejoro el resultado de la configuracion base, y se documentan como resultado negativo.
- `coseno_por_clase.png`: distribucion de similitud de coseno entre pares de texto, agrupada por clase real. Muestra que los pares contradictorios tienen mayor similitud promedio que los pares sin relacion, lo que explica por que la linea base de similitud no funciona en este dominio.
- `metricas_por_clase.png`: precision, recall y F1 por clase para el clasificador NLI zero shot (tres clases).
- `resultados_lora_5clases.csv`: resultados del ajuste fino con LoRA en las cinco clases originales del proyecto, en dos versiones. La primera version (10 epocas, sin ponderacion de clases) colapso hacia la clase mas frecuente del entrenamiento (COMPATIBILIDAD), prediciendola en el 81 por ciento de los casos del gold set. La segunda version (6 epocas, con perdida ponderada por frecuencia inversa de clase) corrigio ese colapso y mejoro accuracy de 0.204 a 0.254 y F1 macro de 0.121 a 0.209.
- `resultados_lora_5clases_reporte_por_clase.csv`: precision, recall y F1 por clase de la version final (con pesos), sobre el gold set de 142 pares.

## Hallazgo principal del ajuste fino con LoRA

La ponderacion de clases corrigio el colapso hacia la clase mayoritaria y mejoro el desempeno en cuatro de las cinco clases (contradiccion, compatibilidad, excepcion, sin relacion). La clase especificacion, sin embargo, obtuvo F1 de 0 tanto antes como despues del ajuste, sin una sola prediccion correcta en 142 casos. Esta clase fallo de forma equivalente en cinco configuraciones experimentales independientes a lo largo del proyecto: modelo NLI en ingles, modelo NLI multilingue zero shot, el mismo modelo sobre un gold set balanceado, con segmentacion de texto largo, y ahora con ajuste fino supervisado de cinco clases. La convergencia de este resultado en configuraciones tan distintas descarta el desbalance de datos o el ruido de una corrida particular como explicacion, y respalda la interpretacion de que existe una divergencia conceptual entre la nocion juridica de especificacion normativa y la representacion que estos modelos aprenden de la relacion de implicacion (entailment).


## Analisis de errores

El patron de error mas consistente observado, repetido en cuatro configuraciones distintas del clasificador zero shot (modelo en ingles, modelo multilingue, gold set balanceado, y con segmentacion de texto largo), es la confusion sistematica de la clase especificacion hacia la clase sin relacion o neutral, con recall cercano a cero en todos los casos. Se interpreta como una divergencia conceptual entre la nocion juridica de especificacion normativa y la definicion operacional de entailment en los modelos NLI convencionales, no como un error de implementacion. El detalle de esta interpretacion esta en `docs/limitaciones.md`.
